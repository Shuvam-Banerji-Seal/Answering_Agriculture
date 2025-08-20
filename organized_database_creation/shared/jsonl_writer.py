#!/usr/bin/env python3
"""
JSONL Writer - Shared utility for writing structured data to JSONL files
"""

import json
import threading
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class JSONLWriter:
    """Thread-safe JSONL file writer"""
    
    def __init__(self, output_file: str):
        self.output_file = Path(output_file)
        self.lock = threading.Lock()
        self.entries_written = 0
        
        # Ensure output directory exists
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
    
    def write_entry(self, entry: Dict[str, Any]) -> bool:
        """Write a single entry to JSONL file"""
        try:
            with self.lock:
                with open(self.output_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
                self.entries_written += 1
            return True
        except Exception as e:
            print(f"Error writing entry: {e}")
            return False
    
    def write_entries(self, entries: List[Dict[str, Any]]) -> int:
        """Write multiple entries to JSONL file"""
        written_count = 0
        with self.lock:
            try:
                with open(self.output_file, 'a', encoding='utf-8') as f:
                    for entry in entries:
                        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
                        written_count += 1
                self.entries_written += written_count
            except Exception as e:
                print(f"Error writing entries: {e}")
        
        return written_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get writer statistics"""
        return {
            'output_file': str(self.output_file),
            'entries_written': self.entries_written,
            'file_exists': self.output_file.exists(),
            'file_size': self.output_file.stat().st_size if self.output_file.exists() else 0
        }


class ImmediateJSONLWriter(JSONLWriter):
    """Immediate JSONL writer for real-time data processing"""
    
    def __init__(self, output_file: str, buffer_size: int = 1):
        super().__init__(output_file)
        self.buffer_size = buffer_size
        self.buffer = []
        self.last_flush = datetime.now()
    
    def write_entry_immediate(self, entry: Dict[str, Any]) -> bool:
        """Write entry immediately without buffering"""
        return self.write_entry(entry)
    
    def write_entry_buffered(self, entry: Dict[str, Any]) -> bool:
        """Write entry with buffering"""
        with self.lock:
            self.buffer.append(entry)
            
            if len(self.buffer) >= self.buffer_size:
                return self._flush_buffer()
        
        return True
    
    def _flush_buffer(self) -> bool:
        """Flush buffer to file"""
        if not self.buffer:
            return True
        
        try:
            with open(self.output_file, 'a', encoding='utf-8') as f:
                for entry in self.buffer:
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            
            self.entries_written += len(self.buffer)
            self.buffer.clear()
            self.last_flush = datetime.now()
            return True
        except Exception as e:
            print(f"Error flushing buffer: {e}")
            return False
    
    def force_flush(self) -> bool:
        """Force flush buffer to file"""
        with self.lock:
            return self._flush_buffer()
    
    def __del__(self):
        """Ensure buffer is flushed on destruction"""
        if hasattr(self, 'buffer') and self.buffer:
            self._flush_buffer()