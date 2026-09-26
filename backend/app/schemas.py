from pydantic import BaseModel, Field


class EmailAnalysisRequest(BaseModel):
    user_id: int = Field(gt=0)
    max_results: int = Field(default=5, ge=1, le=20)
    query: str | None = None


class EmailAnalysisResult(BaseModel):
    email_id: str | None = None
    subject: str
    sender: str
    date: str
    analysis: str


class EmailAnalysisResponse(BaseModel):
    results: list[EmailAnalysisResult]
