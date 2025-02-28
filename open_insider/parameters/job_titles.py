from typing import List, Union, Optional

from open_insider.parameters.validate import validate_list_str_param


class JobTitlesParam:
    
    JOB_TITLE_MAP = {
        "COB": ("Chairman of the Board", "iscob"),
        "CEO": ("Chief Executive Officer", "isceo"),
        "Pres": ("President", "ispres"),
        "COO": ("Chief Operating Officer", "iscoo"),
        "CFO": ("Chief Financial Officer", "iscfo"),
        "GC": ("General Counsel", "isgc"),
        "VP": ("Vice President", "isvp"),
        "Director": ("Director", "isdirector"),
        "10% Owner": ("10% Owner", "istenpercent"),
        "Other": ("Other", "isother"),
    }

    @classmethod
    def validate(cls, job_titles: Optional[Union[str, List[str]]] = None) -> List[str]:
        return validate_list_str_param(
            param_name="job_titles",
            param_value=job_titles,
            options=list(cls.JOB_TITLE_MAP.keys()),
        )

    @classmethod
    def to_url_params(cls, job_titles: List[str] | None) -> str:
        if job_titles is None:
            job_titles = []
        elif isinstance(job_titles, str):
            job_titles = [job_titles]
        return "&".join([f"{cls.JOB_TITLE_MAP[jt][1]}=1" for jt in job_titles])