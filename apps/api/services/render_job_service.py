import time
from typing import Dict, Any, Optional
from pydantic import BaseModel


class RenderJob(BaseModel):
    job_id: str
    project_id: str
    renderer: str
    template_id: str
    status: str  # "queued", "processing", "completed", "failed"
    progress_percentage: int = 0
    stage_message: str = "Queued"
    output_path: Optional[str] = None
    created_at: float = time.time()


class RenderJobService:
    """
    Service for managing background video render jobs and progress streaming.
    """

    _jobs: Dict[str, RenderJob] = {}

    @classmethod
    def create_job(cls, job_id: str, project_id: str, renderer: str, template_id: str) -> RenderJob:
        job = RenderJob(
            job_id=job_id,
            project_id=project_id,
            renderer=renderer,
            template_id=template_id,
            status="queued",
            progress_percentage=0,
            stage_message="Job added to queue"
        )
        cls._jobs[job_id] = job
        return job

    @classmethod
    def update_progress(cls, job_id: str, progress: int, stage_msg: str, status: str = "processing") -> Optional[RenderJob]:
        if job_id in cls._jobs:
            job = cls._jobs[job_id]
            job.progress_percentage = progress
            job.stage_message = stage_msg
            job.status = status
            return job
        return None

    @classmethod
    def get_job(cls, job_id: str) -> Optional[RenderJob]:
        return cls._jobs.get(job_id)
