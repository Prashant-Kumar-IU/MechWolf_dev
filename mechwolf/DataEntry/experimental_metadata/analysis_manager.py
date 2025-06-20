"""
Analysis Data Manager - Handles analytical data and results

This module manages the analysis section of experimental metadata, including
TLC, NMR, GC-MS, yield data, and other analytical results. This is designed
for future expansion as analysis capabilities are added.
"""

from typing import Dict, Any, List, Optional, Union
from .schema_definitions import get_current_timestamp


class AnalysisDataManager:
    """
    Manager for analysis-related experimental data
    
    Handles:
    - TLC data and Rf values
    - Spectroscopy data (NMR, IR, MS, UV-Vis)
    - Chromatography data (GC-MS, HPLC, LC-MS)
    - Yield and purity data
    - Custom analysis types
    """
    
    def __init__(self, metadata_manager):
        """Initialize with reference to main metadata manager"""
        self.metadata_manager = metadata_manager
        self.section_name = "analysis"
    
    def get_data(self) -> Dict[str, Any]:
        """Get the analysis section data"""
        return self.metadata_manager.get_section_data(self.section_name)
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        """Save analysis section data"""
        return self.metadata_manager.update_section_data(self.section_name, data)
    
    # TLC Data Management
    def add_tlc_plate(self, plate_data: Dict[str, Any]) -> bool:
        """
        Add TLC plate data
        
        Args:
            plate_data: Dictionary with plate information
                Optional: plate_id, solvent_system, rf_values, observations, image_path
        
        Returns:
            True if added successfully
        """
        data = self.get_data()
        if "tlc_data" not in data:
            data["tlc_data"] = {"plates": [], "rf_values": {}, "observations": ""}
        if "plates" not in data["tlc_data"]:
            data["tlc_data"]["plates"] = []
        
        # Add timestamp and unique ID
        plate_data["timestamp"] = get_current_timestamp()
        plate_data["id"] = len(data["tlc_data"]["plates"]) + 1
        
        data["tlc_data"]["plates"].append(plate_data)
        return self.save_data(data)
    
    def update_rf_values(self, rf_data: Dict[str, float]) -> bool:
        """
        Update Rf values for compounds
        
        Args:
            rf_data: Dictionary mapping compound names to Rf values
        
        Returns:
            True if updated successfully
        """
        data = self.get_data()
        if "tlc_data" not in data:
            data["tlc_data"] = {"plates": [], "rf_values": {}, "observations": ""}
        
        data["tlc_data"]["rf_values"].update(rf_data)
        return self.save_data(data)
    
    def add_tlc_observations(self, observations: str) -> bool:
        """Add TLC observations"""
        data = self.get_data()
        if "tlc_data" not in data:
            data["tlc_data"] = {"plates": [], "rf_values": {}, "observations": ""}
        
        # Append to existing observations
        existing = data["tlc_data"].get("observations", "")
        if existing:
            data["tlc_data"]["observations"] = f"{existing}\n\n{observations}"
        else:
            data["tlc_data"]["observations"] = observations
        
        return self.save_data(data)
    
    # Spectroscopy Data Management
    def add_nmr_data(self, nmr_data: Dict[str, Any]) -> bool:
        """
        Add NMR spectroscopy data
        
        Args:
            nmr_data: Dictionary with NMR information
                Optional: nucleus, frequency, solvent, peaks, file_path, notes
        
        Returns:
            True if added successfully
        """
        data = self.get_data()
        if "spectroscopy" not in data:
            data["spectroscopy"] = {}
        if "nmr" not in data["spectroscopy"]:
            data["spectroscopy"]["nmr"] = []
        
        nmr_data["timestamp"] = get_current_timestamp()
        data["spectroscopy"]["nmr"].append(nmr_data)
        return self.save_data(data)
    
    def add_ir_data(self, ir_data: Dict[str, Any]) -> bool:
        """Add IR spectroscopy data"""
        data = self.get_data()
        if "spectroscopy" not in data:
            data["spectroscopy"] = {}
        if "ir" not in data["spectroscopy"]:
            data["spectroscopy"]["ir"] = []
        
        ir_data["timestamp"] = get_current_timestamp()
        data["spectroscopy"]["ir"].append(ir_data)
        return self.save_data(data)
    
    def add_ms_data(self, ms_data: Dict[str, Any]) -> bool:
        """Add mass spectrometry data"""
        data = self.get_data()
        if "spectroscopy" not in data:
            data["spectroscopy"] = {}
        if "ms" not in data["spectroscopy"]:
            data["spectroscopy"]["ms"] = []
        
        ms_data["timestamp"] = get_current_timestamp()
        data["spectroscopy"]["ms"].append(ms_data)
        return self.save_data(data)
    
    def add_uv_vis_data(self, uv_data: Dict[str, Any]) -> bool:
        """Add UV-Vis spectroscopy data"""
        data = self.get_data()
        if "spectroscopy" not in data:
            data["spectroscopy"] = {}
        if "uv_vis" not in data["spectroscopy"]:
            data["spectroscopy"]["uv_vis"] = []
        
        uv_data["timestamp"] = get_current_timestamp()
        data["spectroscopy"]["uv_vis"].append(uv_data)
        return self.save_data(data)
    
    # Chromatography Data Management
    def add_gc_ms_data(self, gc_ms_data: Dict[str, Any]) -> bool:
        """Add GC-MS chromatography data"""
        data = self.get_data()
        if "chromatography" not in data:
            data["chromatography"] = {}
        if "gc_ms" not in data["chromatography"]:
            data["chromatography"]["gc_ms"] = []
        
        gc_ms_data["timestamp"] = get_current_timestamp()
        data["chromatography"]["gc_ms"].append(gc_ms_data)
        return self.save_data(data)
    
    def add_hplc_data(self, hplc_data: Dict[str, Any]) -> bool:
        """Add HPLC chromatography data"""
        data = self.get_data()
        if "chromatography" not in data:
            data["chromatography"] = {}
        if "hplc" not in data["chromatography"]:
            data["chromatography"]["hplc"] = []
        
        hplc_data["timestamp"] = get_current_timestamp()
        data["chromatography"]["hplc"].append(hplc_data)
        return self.save_data(data)
    
    def add_lc_ms_data(self, lc_ms_data: Dict[str, Any]) -> bool:
        """Add LC-MS chromatography data"""
        data = self.get_data()
        if "chromatography" not in data:
            data["chromatography"] = {}
        if "lc_ms" not in data["chromatography"]:
            data["chromatography"]["lc_ms"] = []
        
        lc_ms_data["timestamp"] = get_current_timestamp()
        data["chromatography"]["lc_ms"].append(lc_ms_data)
        return self.save_data(data)
    
    # Yield and Purity Data
    def set_yield_data(self, yield_data: Dict[str, Any]) -> bool:
        """
        Set yield and purity data
        
        Args:
            yield_data: Dictionary with yield information
                Optional: theoretical_yield, actual_yield, percent_yield, purity, method
        
        Returns:
            True if set successfully
        """
        data = self.get_data()
        if "yield_data" not in data:
            data["yield_data"] = {}
        
        # Calculate percent yield if not provided
        if ("theoretical_yield" in yield_data and 
            "actual_yield" in yield_data and 
            "percent_yield" not in yield_data):
            theoretical = yield_data["theoretical_yield"]
            actual = yield_data["actual_yield"]
            if theoretical and theoretical > 0:
                yield_data["percent_yield"] = (actual / theoretical) * 100
        
        data["yield_data"].update(yield_data)
        data["yield_data"]["last_updated"] = get_current_timestamp()
        return self.save_data(data)
    
    def update_yield_data(self, updates: Dict[str, Any]) -> bool:
        """Update specific fields in yield data"""
        data = self.get_data()
        if "yield_data" not in data:
            data["yield_data"] = {}
        
        data["yield_data"].update(updates)
        data["yield_data"]["last_updated"] = get_current_timestamp()
        return self.save_data(data)
    
    # Custom Analysis Types
    def add_custom_analysis(self, analysis_type: str, analysis_data: Dict[str, Any]) -> bool:
        """
        Add custom analysis data
        
        Args:
            analysis_type: Name of the analysis type
            analysis_data: Analysis data dictionary
        
        Returns:
            True if added successfully
        """
        data = self.get_data()
        if "custom_analysis" not in data:
            data["custom_analysis"] = {}
        if analysis_type not in data["custom_analysis"]:
            data["custom_analysis"][analysis_type] = []
        
        analysis_data["timestamp"] = get_current_timestamp()
        data["custom_analysis"][analysis_type].append(analysis_data)
        return self.save_data(data)
    
    def update_custom_analysis_type(self, analysis_type: str, type_data: Dict[str, Any]) -> bool:
        """Update an entire custom analysis type"""
        data = self.get_data()
        if "custom_analysis" not in data:
            data["custom_analysis"] = {}
        
        data["custom_analysis"][analysis_type] = type_data
        return self.save_data(data)
    
    # Query Methods
    def get_tlc_data(self) -> Dict[str, Any]:
        """Get all TLC data"""
        data = self.get_data()
        return data.get("tlc_data", {})
    
    def get_spectroscopy_data(self, technique: Optional[str] = None) -> Dict[str, Any]:
        """
        Get spectroscopy data
        
        Args:
            technique: Specific technique ("nmr", "ir", "ms", "uv_vis") or None for all
        
        Returns:
            Spectroscopy data dictionary
        """
        data = self.get_data()
        spectroscopy = data.get("spectroscopy", {})
        
        if technique:
            return spectroscopy.get(technique, [])
        return spectroscopy
    
    def get_chromatography_data(self, technique: Optional[str] = None) -> Dict[str, Any]:
        """
        Get chromatography data
        
        Args:
            technique: Specific technique ("gc_ms", "hplc", "lc_ms") or None for all
        
        Returns:
            Chromatography data dictionary
        """
        data = self.get_data()
        chromatography = data.get("chromatography", {})
        
        if technique:
            return chromatography.get(technique, [])
        return chromatography
    
    def get_yield_data(self) -> Dict[str, Any]:
        """Get yield and purity data"""
        data = self.get_data()
        return data.get("yield_data", {})
    
    def get_custom_analysis(self, analysis_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get custom analysis data
        
        Args:
            analysis_type: Specific analysis type or None for all
        
        Returns:
            Custom analysis data
        """
        data = self.get_data()
        custom = data.get("custom_analysis", {})
        
        if analysis_type:
            return custom.get(analysis_type, [])
        return custom
    
    def get_analysis_summary(self) -> Dict[str, int]:
        """Get summary of available analysis data"""
        data = self.get_data()
        summary = {}
        
        # Count TLC plates
        tlc_data = data.get("tlc_data", {})
        summary["tlc_plates"] = len(tlc_data.get("plates", []))
        
        # Count spectroscopy data
        spectroscopy = data.get("spectroscopy", {})
        for technique in ["nmr", "ir", "ms", "uv_vis"]:
            summary[f"{technique}_spectra"] = len(spectroscopy.get(technique, []))
        
        # Count chromatography data
        chromatography = data.get("chromatography", {})
        for technique in ["gc_ms", "hplc", "lc_ms"]:
            summary[f"{technique}_runs"] = len(chromatography.get(technique, []))
        
        # Check yield data
        yield_data = data.get("yield_data", {})
        summary["yield_data_available"] = 1 if yield_data else 0
        
        # Count custom analysis types
        custom = data.get("custom_analysis", {})
        summary["custom_analysis_types"] = len(custom)
        
        return summary
    
    # Validation
    def validate_analysis_data(self) -> List[str]:
        """Validate analysis data and return any issues"""
        issues = []
        data = self.get_data()
        
        # Check yield data consistency
        yield_data = data.get("yield_data", {})
        if yield_data:
            theoretical = yield_data.get("theoretical_yield")
            actual = yield_data.get("actual_yield")
            percent = yield_data.get("percent_yield")
            
            if theoretical and actual and percent:
                calculated_percent = (actual / theoretical) * 100
                if abs(calculated_percent - percent) > 0.1:  # Allow small rounding differences
                    issues.append(f"Percent yield mismatch: calculated {calculated_percent:.1f}% vs recorded {percent:.1f}%")
            
            if actual and theoretical and actual > theoretical:
                issues.append("Actual yield exceeds theoretical yield")
            
            if percent and (percent < 0 or percent > 100):
                issues.append(f"Invalid percent yield: {percent}%")
        
        # Check Rf values
        tlc_data = data.get("tlc_data", {})
        rf_values = tlc_data.get("rf_values", {})
        for compound, rf in rf_values.items():
            if not isinstance(rf, (int, float)) or rf < 0 or rf > 1:
                issues.append(f"Invalid Rf value for {compound}: {rf} (should be 0-1)")
        
        return issues
    
    # Bulk Operations
    def clear_analysis_type(self, analysis_type: str) -> bool:
        """
        Clear all data for a specific analysis type
        
        Args:
            analysis_type: Type to clear ("tlc", "spectroscopy", "chromatography", "yield", "custom")
        
        Returns:
            True if cleared successfully
        """
        data = self.get_data()
        
        if analysis_type == "tlc":
            data["tlc_data"] = {"plates": [], "rf_values": {}, "observations": ""}
        elif analysis_type == "spectroscopy":
            data["spectroscopy"] = {}
        elif analysis_type == "chromatography":
            data["chromatography"] = {}
        elif analysis_type == "yield":
            data["yield_data"] = {}
        elif analysis_type == "custom":
            data["custom_analysis"] = {}
        else:
            print(f"❌ Unknown analysis type: {analysis_type}")
            return False
        
        return self.save_data(data)
    
    def export_analysis_summary(self) -> str:
        """Export a human-readable analysis summary"""
        data = self.get_data()
        summary_counts = self.get_analysis_summary()
        
        summary = f"""
🔬 Analysis Summary
══════════════════
📊 Data Overview:
   • TLC Plates: {summary_counts.get('tlc_plates', 0)}
   • NMR Spectra: {summary_counts.get('nmr_spectra', 0)}
   • IR Spectra: {summary_counts.get('ir_spectra', 0)}
   • MS Spectra: {summary_counts.get('ms_spectra', 0)}
   • UV-Vis Spectra: {summary_counts.get('uv_vis_spectra', 0)}
   • GC-MS Runs: {summary_counts.get('gc_ms_runs', 0)}
   • HPLC Runs: {summary_counts.get('hplc_runs', 0)}
   • LC-MS Runs: {summary_counts.get('lc_ms_runs', 0)}
   • Custom Analysis Types: {summary_counts.get('custom_analysis_types', 0)}

🎯 Yield Data:
        """
        
        yield_data = data.get("yield_data", {})
        if yield_data:
            summary += f"\n   • Theoretical Yield: {yield_data.get('theoretical_yield', 'Not specified')}"
            summary += f"\n   • Actual Yield: {yield_data.get('actual_yield', 'Not specified')}"
            summary += f"\n   • Percent Yield: {yield_data.get('percent_yield', 'Not calculated')}%"
            summary += f"\n   • Purity: {yield_data.get('purity', 'Not specified')}"
            summary += f"\n   • Method: {yield_data.get('method', 'Not specified')}"
        else:
            summary += "\n   • No yield data recorded"
        
        # TLC Summary
        tlc_data = data.get("tlc_data", {})
        if tlc_data.get("rf_values"):
            summary += "\n\n📋 TLC Rf Values:"
            for compound, rf in tlc_data["rf_values"].items():
                summary += f"\n   • {compound}: {rf}"
        
        return summary.strip()