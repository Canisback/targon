from targon.templates.match_template import *

# Set server and API key
targon.set_server("euw1")
targon.set_api_key("RGAPI-XXXX")

# Set limitation in matchlist (highly recommended)
matchlist.set_input_args({"beginTime":1618358400000,"endTime":1618444800000,"queue":420})

# Set the number of callers (recommended to reach methods limits with production rate limits)
#match.set_n_callers(50)
#matchlist.set_n_callers(100)

# Set the number of callers (recommended for development keys limits focusing on match data)
match.set_n_callers(10)
matchlist.set_n_callers(1)

# Simple callback function thjat will print all
def simple_callback(matchId, match_data):
    print("MatchId : ", matchId)
    print("Match data : ", match_data)
    # This is the custom part where you put the code you want run on the data
    # For instance : 
    # database.insert(match_data)
    
# Plug in the callback function
match.add_callback(simple_callback)

# Run targon
targon.run()