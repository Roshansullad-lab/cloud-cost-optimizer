from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
import io
import json
from database import SessionLocal, engine, Base, OrphanedResource
#import database

app = FastAPI(
    title="FinOps Cloud Cost Optimizer & Remediation Engine",
    version="1.0.0",
    description="API-first engine to ingest billing/inventory data, detect waste, and generate CLI remediation scripts."
)

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper: Generate Cloud-Specific Remediation CLI
def generate_cli_command(provider: str, r_type: str, r_id: str, region: str) -> str:
    if provider.upper() == "AWS":
        if r_type == "volume":
            return f"aws ec2 delete-volume --volume-id {r_id} --region {region}"
        elif r_type == "vm":
            return f"aws ec2 terminate-instances --instance-ids {r_id} --region {region}"
            
    elif provider.upper() == "AZURE":
        if r_type == "volume": # Managed Disk
            return f"az disk delete --ids {r_id} --yes"
        elif r_type == "vm":
            return f"az vm delete --ids {r_id} --yes"
            
    return "# Resource type or provider fallback not generated automatically."

# --- API ENDPOINTS ---

@app.post("/import/inventory/", tags=["Ingestion"])
async def import_inventory(
    cloud_provider: str, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    """
    Ingests a CSV inventory/billing export. 
    Expected columns: resource_id, resource_type, region, status, monthly_cost
    """
    if cloud_provider.upper() not in ["AWS", "AZURE"]:
        raise HTTPException(status_code=400, detail="Invalid cloud provider. Use 'AWS' or 'Azure'.")

    contents = await file.read()
    
    try:
        # Read dynamically whether CSV or JSON
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith('.json'):
            df = pd.read_json(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV or JSON.")
    except Exception as e:
        raise HTTPException(status_code=420, detail=f"Error parsing file: {str(e)}")

    detected_waste_count = 0

    # FinOps Engine Rules Engine Logic
    for _, row in df.iterrows():
        is_orphaned = False
        
        # Rule 1: Unattached/Available storage disks
        if row['resource_type'] == 'volume' and row['status'] in ['available', 'Unattached']:
            is_orphaned = True
            
        # Rule 2: Idle Virtual Machines (Simulated flag from metrics export)
        elif row['resource_type'] == 'vm' and row['status'] in ['idle', 'stopped']:
            is_orphaned = True

        if is_orphaned:
            # Check if already exists in DB to prevent duplicates
            exists = db.query(OrphanedResource).filter_by(resource_id=row['resource_id']).first()
            if not exists:
                new_waste = OrphanedResource(
                    cloud_provider=cloud_provider.upper(),
                    resource_id=row['resource_id'],
                    resource_type=row['resource_type'],
                    region=row['region'],
                    estimated_monthly_waste=float(row.get('monthly_cost', 0.0)),
                    status="Detected"
                )
                db.add(new_waste)
                detected_waste_count += 1
                
    db.commit()
    return {"message": "Ingestion successful", "orphaned_resources_detected": detected_waste_count}


@app.get("/optimize/", tags=["FinOps Engine"])
def get_optimization_dashboard(db: Session = Depends(get_db)):
    """
    Returns all active orphaned resources and aggregates total potential savings.
    """
    resources = db.query(OrphanedResource).filter_by(status="Detected").all()
    total_savings = sum(r.estimated_monthly_waste for r in resources)
    
    return {
        "total_potential_monthly_savings_usd": round(total_savings, 2),
        "resource_count": len(resources),
        "resources": resources
    }


@app.get("/optimize/remediation-script/", tags=["Remediation"])
def generate_remediation_script(cloud_provider: str, db: Session = Depends(get_db)):
    """
    Generates a ready-to-execute Shell script containing CLI commands 
    to delete all detected orphaned resources for a specific cloud provider.
    """
    resources = db.query(OrphanedResource).filter_by(
        cloud_provider=cloud_provider.upper(), 
        status="Detected"
    ).all()
    
    if not resources:
        return {"script": "# No orphaned resources detected for this provider."}
        
    script_lines = [
        f"#!/bin/bash",
        f"# Automated FinOps Remediation Script for {cloud_provider.upper()}",
        f"# Generated at: {pd.Timestamp.now()}",
        ""
    ]
    
    for res in resources:
        cli_cmd = generate_cli_command(res.cloud_provider, res.resource_type, res.resource_id, res.region)
        script_lines.append(f"# Potential Savings: ${res.estimated_monthly_waste}/mo")
        script_lines.append(cli_cmd)
        script_lines.append("")
        
    return {
        "cloud_provider": cloud_provider.upper(),
        "target_resources_count": len(resources),
        "script": "\n".join(script_lines)
    }