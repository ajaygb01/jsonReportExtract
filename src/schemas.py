from typing import List, Optional
from pydantic import BaseModel, Field

class BloodReportItem(BaseModel):
    name: str = Field(description="The name of the test or biomarker, e.g., 'Hemoglobin', 'WBC Count'.")
    value: str = Field(description="The exact numerical value or result text extracted from the report.")
    measure: Optional[str] = Field(description="The unit of measurement used, e.g., 'g/dL', '10^9/L', if available.")
    normal_valuelimit: Optional[str] = Field(description="The reference range or normal limit specified in the report, if available.")
    comments: Optional[str] = Field(description="Any specific comments, flags (e.g., 'High', 'Low'), or interpretations directly associated with this test.")

class BloodReportExtraction(BaseModel):
    items: List[BloodReportItem] = Field(description="List of all extracted blood report values and biomarkers.")
    general_comments: Optional[str] = Field(description="Any general remarks, doctor's notes, or overarching comments found at the end or beginning of the report.")
