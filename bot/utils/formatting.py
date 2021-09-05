from typing import Optional


def codeblock(content: str, max_size: int = 1024, fmt: Optional[str] = 'py') -> Optional[str]:
    max_size -= 8 + len(fmt or '')
    if not content:
        return 'N/A'

    if len(content) > max_size:
        content = content[:max_size - 1] + '…'

    if fmt:
        return f'```{fmt}\n{content}\n```'

    return f'```{content}```'
