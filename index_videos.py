#!/usr/bin/env python3
"""
Video Indexer - Main Script

Orchestrates all modules to index videos and create searchable database.
This is the main entry point for Phase 1 (indexing).
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.data_models import ScoreMetrics, VideoSegment, VideoMetadata, IndexMetadata
from core.video_reader import VideoReader
from core.segment_processor import SegmentProcessor


class VideoIndexer:
    """
    Main indexer that coordinates video reading and segment processing.
    
    Indexes all videos in a folder by analyzing segments and storing metrics.
    """
    
    def __init__(self, segment_duration: float = 1.0):
        """
        Initialize the video indexer.
        
        Args:
            segment_duration: Duration of each segment in seconds (default: 1.0)
        """
        self.segment_duration = segment_duration
        self.processor = SegmentProcessor()
    
    def index_video(self, video_path: Path) -> List[VideoSegment]:
        """
        Index a single video file.
        
        Reads the video in segments, calculates metrics for each segment,
        and returns a list of VideoSegment objects.
        
        Args:
            video_path: Path to video file
            
        Returns:
            List of VideoSegment objects with calculated metrics
        """
        print(f"  Indexing {video_path.name}")
        
        # Initialize video reader
        reader = VideoReader(video_path)
        metadata = reader.get_metadata()
        
        print(f"  Duration: {metadata['duration']:.1f}s, FPS: {metadata['fps']:.1f}")
        
        segments = []
        segment_count = 0
        
        # Iterate through all segments in the video
        for start_frame, frames in reader.iterate_segments(self.segment_duration):
            # Calculate metrics for this segment
            metrics = self.processor.process_segment(frames)
            
            # Calculate timing
            fps = metadata['fps']
            start_time = start_frame / fps
            end_time = start_time + self.segment_duration
            
            # Create segment object
            segment = VideoSegment(
                video_file=video_path.name,
                start_time=start_time,
                end_time=end_time,
                duration=self.segment_duration,
                metrics=metrics
            )
            
            segments.append(segment)
            segment_count += 1
        
        print(f"  Indexed {segment_count} segments")
        return segments
    
    def index_folder(self, input_folder: Path, output_file: Path) -> Dict:
        """
        Index all videos in a folder.
        
        Processes all supported video files in the folder and creates
        a comprehensive JSON index with all metrics.
        
        Args:
            input_folder: Path to folder containing videos
            output_file: Path to output JSON file
            
        Returns:
            Dictionary containing the complete index
        """
        # Find all video files
        video_files = VideoReader.find_videos(input_folder)
        
        if not video_files:
            print(f"No video files found in {input_folder}")
            return {}
        
        print(f"\nFound {len(video_files)} videos to index")
        print(f"Segment duration: {self.segment_duration}s\n")
        
        all_segments = []
        video_metadata = {}
        
        # Process each video
        for idx, video_file in enumerate(video_files, 1):
            print(f"[{idx}/{len(video_files)}]")
            
            try:
                # Index this video
                segments = self.index_video(video_file)
                all_segments.extend(segments)
                
                # Store metadata
                video_metadata[video_file.name] = VideoMetadata(
                    segment_count=len(segments),
                    file_path=str(video_file),
                    indexed=True
                ).to_dict()
                
                print(f"  ✓ Completed\n")
                
            except Exception as e:
                print(f"  ✗ Error: {e}\n")
                video_metadata[video_file.name] = VideoMetadata(
                    segment_count=0,
                    file_path=str(video_file),
                    indexed=False,
                    error=str(e)
                ).to_dict()
        
        # Create index metadata
        index_metadata = IndexMetadata(
            created_at=datetime.now().isoformat(),
            segment_duration=self.segment_duration,
            total_segments=len(all_segments),
            total_videos=len(video_files),
            indexed_videos=sum(1 for v in video_metadata.values() if v['indexed']),
            available_metrics=list(ScoreMetrics().__dict__.keys())
        )
        
        # Build complete index structure
        index = {
            'metadata': index_metadata.to_dict(),
            'videos': video_metadata,
            'segments': [seg.to_dict() for seg in all_segments]
        }
        
        # Save to JSON file
        self._save_index(index, output_file)
        
        # Print summary
        self._print_summary(index)
        
        return index
    
    def _save_index(self, index: Dict, output_file: Path):
        """
        Save index to JSON file.
        
        Args:
            index: Index dictionary
            output_file: Output file path
        """
        print(f"Saving index to {output_file}")
        
        # Create parent directories if needed
        output_file.parent.mkdir(exist_ok=True, parents=True)
        
        # Write JSON with indentation for readability
        with open(output_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def _print_summary(self, index: Dict):
        """
        Print summary of indexing results.
        
        Args:
            index: Complete index dictionary
        """
        metadata = index['metadata']
        
        print(f"\n{'='*60}")
        print(f"✓ Indexing Complete!")
        print(f"{'='*60}")
        print(f"Total segments indexed: {metadata['total_segments']}")
        print(f"Videos processed: {metadata['indexed_videos']}/{metadata['total_videos']}")
        print(f"Segment duration: {metadata['segment_duration']}s")
        print(f"Available metrics: {', '.join(metadata['available_metrics'])}")
        print(f"{'='*60}\n")


def main():
    """Main entry point for the video indexer"""
    
    parser = argparse.ArgumentParser(
        description="Index videos by analyzing and storing all metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Index videos with 1-second segments (default)
  %(prog)s input_videos/ video_index.json
  
  # Index with 0.5-second segments for finer granularity
  %(prog)s input_videos/ video_index.json --segment-duration 0.5
  
  # Index with 2-second segments for faster processing
  %(prog)s input_videos/ video_index.json -d 2.0

This creates a searchable index that can be queried later without re-processing videos.

Supported formats: .mp4, .mov, .avi, .mkv, .m4v, .flv, .wmv

Modular Metrics System:
  Each metric is in its own file in the metrics/ folder.
  Easy to add, remove, or modify individual metrics.
        """
    )
    
    parser.add_argument(
        "input_folder",
        help="Folder containing input videos"
    )
    parser.add_argument(
        "output_file",
        help="Output JSON file for the index (e.g., video_index.json)"
    )
    parser.add_argument(
        "-d", "--segment-duration",
        type=float,
        default=1.0,
        help="Duration of each indexed segment in seconds (default: 1.0)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    input_path = Path(args.input_folder)
    if not input_path.exists():
        parser.error(f"Input folder does not exist: {args.input_folder}")
    
    if not input_path.is_dir():
        parser.error(f"Input path is not a directory: {args.input_folder}")
    
    if args.segment_duration <= 0:
        parser.error("Segment duration must be positive")
    
    if args.segment_duration > 10:
        print("Warning: Large segment duration (>10s) may reduce search granularity")
    
    output_path = Path(args.output_file)
    
    # Create indexer and process videos
    print(f"\nVideo Indexer - Modular Metrics System")
    print(f"{'='*60}\n")
    
    indexer = VideoIndexer(segment_duration=args.segment_duration)
    indexer.index_folder(input_path, output_path)


if __name__ == "__main__":
    main()
