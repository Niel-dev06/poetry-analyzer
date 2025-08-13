# poetry_analyzer.py
import re
import argparse
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Tuple, Union

# CORE ANALYSIS 
@dataclass
class PoemAnalysis:
    meter: List[Dict]
    rhyme_scheme: str
    devices: Dict[str, List[str]]
    sentiment: Dict[str, float]

class PoetryAnalyzer:
    def __init__(self):
        self.positive_words = {'love', 'happy', 'joy', 'peace', 'beautiful', 'sweet', 'good'}
        self.negative_words = {'hate', 'sad', 'pain', 'war', 'ugly', 'bitter', 'bad'}
    
    def analyze(self, text: str) -> PoemAnalysis:
        """Main analysis entry point""" if not text.strip():
            raise ValueError("Empty text provided for analysis")
            
        return PoemAnalysis(
            meter=self._analyze_meter(text),
            rhyme_scheme=self._analyze_rhyme(text),
            devices=self._analyze_devices(text),
            sentiment=self._analyze_sentiment(text))
    
    def _get_lines(self, text: str) -> List[str]:
        """Split text into non-empty lines"""
        return [line.strip() for line in text.split('\n') if line.strip()]
    
    def _get_words(self, text: str) -> List[str]:
        """Extract words from text"""
        return re.findall(r"[a-zA-Z']+", text.lower())
    
    def _count_syllables(self, word: str) -> int:
        """Approximate syllable counting"""
        word = word.lower()
        if word.endswith("e"):
            word = word[:-1]
        vowels = re.findall(r"[aeiouy]+", word)
        return max(1, len(vowels))
       def _analyze_meter(self, text: str) -> List[Dict]:
        """Analyze syllable patterns"""
        analysis = []
        for line in self._get_lines(text):
            words = self._get_words(line)
            syllables = sum(self._count_syllables(word) for word in words)
            analysis.append({
                'line': line,
                'syllables': syllables,
                'pattern': '0' * syllables  # Simplified pattern
            })
        return analysis
    
    def _get_ending(self, line: str) -> str:
        """Get the ending sound of a line"""
        words = self._get_words(line)
        if not words:
            return ""
        last_word = words[-1]
        return last_word[-3:]  # Last 3 letters as rhyme key
    
    def _create_scheme(self, endings: List[str]) -> str:
        """Generate rhyme scheme (AABB, ABAB, etc.)"""
        scheme = []
        rhyme_map = {}
        current_char = ord('A')
        
        for ending in endings:
            if ending not in rhyme_map:
                rhyme_map[ending] = chr(current_char)
                current_char += 1
            scheme.append(rhyme_map[ending])
        return ''.join(scheme)
    
    def _analyze_rhyme(self, text: str) -> str:
        """Determine rhyme scheme"""
        lines = self._get_lines(text)
        endings = [self._get_ending(line) for line in lines]
        return self._create_scheme(endings)
    
    def _find_alliteration(self, words: List[str]) -> List[str]:
        """Detect alliteration (repeated initial sounds)"""
        devices = []
        for i in range(len(words)-1):
            if words[i][0] == words[i+1][0]:
                devices.append(f"{words[i]} {words[i+1]}")
        return devices
    
    def _find_assonance(self, words: List[str]) -> List[str]:
        """Detect assonance (repeated vowel sounds)"""
        devices = []
        vowels = "aeiouy"
        for i in range(len(words)-1):
            word1_vowels = [c for c in words[i] if c in vowels]
            word2_vowels = [c for c in words[i+1] if c in vowels]
            if word1_vowels and word2_vowels and word1_vowels[-1] == word2_vowels[-1]:
                devices.append(f"{words[i]} {words[i+1]}")
        return devices
    
    def _find_metaphors(self, words: List[str]) -> List[str]:
        """Simple metaphor detection"""
        devices = []
        for i in range(len(words)-1):
            if len(words[i]) > 3 and len(words[i+1]) > 3:
                devices.append(f"{words[i]} is like {words[i+1]}")
        return devices
    
    def _analyze_devices(self, text: str) -> Dict[str, List[str]]:
        """Detect literary devices"""
        words = self._get_words(text)
        return {
            'alliteration': self._find_alliteration(words),
            'assonance': self._find_assonance(words),
            'metaphor': self._find_metaphors(words)
        }
    
    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Basic sentiment analysis"""
        words = self._get_words(text)
        pos = sum(1 for w in words if w in self.positive_words)
        neg = sum(1 for w in words if w in self.negative_words)
        total = pos + neg
        polarity = (pos - neg) / total if total > 0 else 0
        return {'polarity': round(polarity, 2), 'positive': pos, 'negative': neg}

# FILE HANDLING
def read_poem(file_path: Union[str, Path]) -> str:
    """Read poem text from file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Poem file not found: {file_path}")
    except UnicodeDecodeError:
        raise ValueError(f"Could not decode file: {file_path}")
def write_analysis(output_path: Union[str, Path], analysis: dict):
    """Write analysis results to file"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(str(analysis))
    except IOError as e:
        raise IOError(f"Failed to write analysis: {e}")


#COMMAND LINE INTERFACE
def run_cli():
    """Run the command line interface"""
    parser = argparse.ArgumentParser(
        description="Poetry Analysis Tool (IDLE Compatible)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('input_file', type=str, help='Poem file to analyze')
    parser.add_argument('-o', '--output', type=str, help='Output file for results')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed analysis')
    
    args = parser.parse_args()
    analyzer = PoetryAnalyzer()
    
    try:
        poem = read_poem(args.input_file)
        analysis = analyzer.analyze(poem)
        
        if args.output:
            write_analysis(args.output, analysis.__dict__)
            print(f"Analysis saved to {args.output}")
        
        if args.verbose or not args.output:
            print("\n=== Poetry Analysis Results ===")
            print(f"\nRhyme Scheme: {analysis.rhyme_scheme}")
            
            print("\nMeter Analysis:")
            for line in analysis.meter:
                print(f"{line['syllables']} syllables: {line['line']}")
            
            print("\nLiterary Devices:")
            for device, examples in analysis.devices.items():
                if examples:
                    print(f"\n{device.capitalize()}:")
                    for example in examples[:3]:  # Show first 3 examples
                        print(f"- {example}")
            
            print("\nSentiment Analysis:")
            print(f"Polarity: {analysis.sentiment['polarity']} (-1 to 1)")
            print(f"Positive words: {analysis.sentiment['positive']}")
            print(f"Negative words: {analysis.sentiment['negative']}")
    
    except Exception as e:
        print(f"\nError: {e}")
        print("\nUsage example:")
        print("python poetry_analyzer.py poem.txt -o results.txt -v")

# IDLE-FRIENDLY INTERFACE
def run_in_idle():
    """Alternative interface for running in IDLE"""
    print("=== Poetry Analyzer ===")
    print("1. Analyze a poem file")
    print("2. Enter poem interactively")
    print("3. Exit")
    
    analyzer = PoetryAnalyzer()
    
    while True:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            file_path = input("Enter poem file path: ").strip()
            try:
                poem = read_poem(file_path)
                analysis = analyzer.analyze(poem)
                
                print("\nAnalysis Results:")
                print(f"Rhyme Scheme: {analysis.rhyme_scheme}")
                print("\nLine Syllable Counts:")
                for line in analysis.meter:
                    print(f"{line['syllables']}: {line['line']}")
                
                save = input("\nSave results to file? (y/n): ").lower()
                if save == 'y':
                    output_path = input("Enter output file path: ")
                    write_analysis(output_path, analysis.__dict__)
                    print("Results saved!")
            
            except Exception as e:
                print(f"Error: {e}")
        
        elif choice == '2':
            print("Enter your poem (press Enter twice to finish):")
            lines = []
            while True:
                line = input()
                if line == "" and lines and lines[-1] == "":
                    break
                lines.append(line)
            poem = "\n".join(lines[:-1])  # Remove last empty line
            
            try:
                analysis = analyzer.analyze(poem)
                print("\nAnalysis Results:")
                print(f"Rhyme Scheme: {analysis.rhyme_scheme}")
                print("\nLiterary Devices Found:")
                for device, examples in analysis.devices.items():
                    if examples:
                        print(f"{device.capitalize()}: {', '.join(examples[:3])}")
            except Exception as e:
                print(f"Error: {e}")
        
        elif choice == '3':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

# MAIN ENTRY POINT
if __name__ == "__main__":
    try:
        # Try to run as CLI if arguments are passed
        import sys
        if len(sys.argv) > 1:
            run_cli()
        else:
            # Fall back to IDLE-friendly interface
            run_in_idle()
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Falling back to IDLE interface...")
        run_in_idle()
