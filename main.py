"""
Imscribing Grammar Main Entry Point

Provides two CLI entry points:
- imscrbgrmr: Full command name
- imscribe: Short alias

Also exposes the agent framework for direct usage.
"""
from imscrbgrmr.cli import main, imscribe_alias

# Export both CLI entry points
imscrbgrmr = main
imscribe = imscribe_alias

if __name__ == "__main__":
    # Default to main CLI
    main()
