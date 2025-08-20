"""
Main CLI interface for sub-query generation.
"""

import argparse
import json
import sys
from pathlib import Path
from .factory import SubQueryGeneratorFactory


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Generate sub-queries for RAG operations")
    parser.add_argument("query", help="The original query to expand")
    parser.add_argument(
        "--config", 
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)"
    )
    parser.add_argument(
        "--output",
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--format",
        choices=["json", "text", "list"],
        default="json",
        help="Output format (default: json)"
    )
    parser.add_argument(
        "--implementation",
        choices=["ollama", "huggingface"],
        help="Override implementation from config"
    )
    parser.add_argument(
        "--check-availability",
        action="store_true",
        help="Check which implementations are available"
    )
    
    args = parser.parse_args()
    
    # Check availability if requested
    if args.check_availability:
        implementations = SubQueryGeneratorFactory.get_available_implementations()
        print("Available implementations:")
        for impl, available in implementations.items():
            status = "✓" if available else "✗"
            print(f"  {status} {impl}")
        return
    
    try:
        # Load configuration
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"Error: Configuration file {config_path} not found", file=sys.stderr)
            sys.exit(1)
        
        # Override implementation if specified
        config_dict = None
        if args.implementation:
            import yaml
            with open(config_path, 'r') as f:
                config_dict = yaml.safe_load(f)
            config_dict['model']['implementation'] = args.implementation
        
        # Create generator
        generator = SubQueryGeneratorFactory.create_generator(
            config_path=str(config_path) if config_dict is None else None,
            config_dict=config_dict
        )
        
        # Check if generator is available
        if not generator.is_available():
            print(f"Error: Generator is not available. Check your configuration and dependencies.", file=sys.stderr)
            sys.exit(1)
        
        # Generate sub-queries
        result = generator.generate_sub_queries(args.query)
        
        # Format output
        if args.format == "json":
            output = json.dumps(result.to_dict(), indent=2)
        elif args.format == "text":
            output = f"Original Query: {result.original_query}\n\nSub-queries:\n"
            for i, query in enumerate(result.sub_queries, 1):
                output += f"{i}. {query}\n"
        elif args.format == "list":
            output = "\n".join(result.sub_queries)
        
        # Write output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Output written to {args.output}")
        else:
            print(output)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()