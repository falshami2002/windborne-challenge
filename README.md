I wrote a Python program that combines the provided Windborne balloon position data with wind speed and direction data from the Open-Meteo API.  
The goal is to estimate how much each balloon had to actively move (steer) to reach its next recorded position, accounting for the surrounding wind conditions.

I made the assumption that the balloons data is always in the same order every time the API is called for each hour as I didn't have a balloon id to reference. After reviewing the data briefly, that appears to be true across the board. 

This concept mirrors what I imagine Windborne might do internally, using real-time wind data to determine how their balloons should adjust to reach desired regions efficiently.  

Currently, the code processes the past 2 hours and only the first 100 balloons per hour to respect Open-Meteo’s fair-use API limits.  

How to Run  
python -m venv .venv  
. .venv/bin/activate          # Windows: .venv\Scripts\activate  
pip install -r requirements.txt  
python main.py  

Output  
All results are saved to balloon_control_vectors.csv, which includes:  
control_magnitude → the estimated speed (m/s) the balloon must actively move relative to the wind.  
bearing → the direction (in degrees clockwise from north) the balloon is moving toward.  
These two columns together represent the magnitude and direction of the control effort each balloon needed to reach its next position.  
