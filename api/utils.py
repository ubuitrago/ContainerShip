import logging

logger = logging.getLogger("uvicorn")

DOCKERFILE_RESERVED_INSTRUCTIONS = set([
    "FROM", "RUN", "CMD", "LABEL", "EXPOSE", "ENV", "ADD", 
    "COPY","ENTRYPOINT", "VOLUME", "USER", "WORKDIR", "ARG",
    "ONBUILD", "HEALTHCHECK", "SHELL", "STOPSIGNAL", # "MAINTAINER", "COMMENT"
])

def line_starts_with_reserved_instruction(line: str) -> bool:
    return any(line.lstrip().startswith(instr) for instr in DOCKERFILE_RESERVED_INSTRUCTIONS)
