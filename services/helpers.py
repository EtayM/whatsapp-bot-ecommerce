def truncate(text, max_length=35):
    if len(text) <= max_length:
        return text
    
    words = text.split()
    truncated = ""
    
    for word in words:
        if len(truncated) + len(word) + (1 if truncated else 0) > max_length:
            break
        truncated += (" " if truncated else "") + word

    return truncated + "..." if truncated else text[:max_length] + "..."