Output earthscope_seismograph_demo.mp4

Set Theme "Catppuccin Frappe"
Set Width 1200
Set Height 1200
Set Shell bash

Type "claude --dangerously-skip-permissions"
Enter
Sleep 5s
Show

Type "Use the ndp-mcp to find the latest dataset of the earthscope organization, find the URLs of the geojson and csv files they contain, and curl them to download locally. "
Type "Context: The geojson file contains metadata about the seismic event. The csv file contains seismograph data (time series measurements). "
Type "Steps: "
Type "1. Use ndp-mcp to search for and identify the latest earthscope dataset. "
Type "2. Extract the URLs for both the geojson (metadata) and csv (seismograph data) files. "
Type "3. Download both files using curl. "
Type "4. Use pandas-mcp to: Load and explore the csv seismograph data, identify the columns/axes in the data, understand the data structure and ranges. Convert time columns to proper datetime format. "
Type "5. Use plot-mcp to: Create individual line plots for each axis in the seismograph data, explore the time series patterns. "
Type "6. Create a final comprehensive visualization: Use uv to manage dependencies for a Python script. Combine all axes as subplots in a single figure. "
Type "IMPORTANT: Format the x-axis time labels to be clean and readable - use proper datetime formatting, rotate labels if needed, and use appropriate time intervals (e.g., HH:MM:SS or relative seconds from start). "
Type "Incorporate relevant metadata from the geojson file (location, magnitude, time, depth, etc.) in the title and annotations. "
Type "Include proper axis labels, clean time formatting on x-axis, titles, and legends. Make the visualization publication-quality with all available context. "
Type "The final output should be a single, information-rich plot with readable time axis that tells the complete story of the seismic event."
Enter
Sleep 240s
