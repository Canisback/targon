from targon.savers import Saver
from targon.queues import Queue, CachedInQueue
from targon.callers import Match, Matchlist
from targon.targon import Targon
from targon.bootstrap import AccountIdSeeder
from targon.parsers import MatchParser, MatchlistParser

# Create the callers
match = Match()
matchlist = Matchlist()

# Create the parsers
# MatchlistParser extracts gameId from a matchlist
matchlist_parser = MatchlistParser()
# MatchParser extracts currentAccountId from a match
match_parser = MatchParser()

# Queues needed to pass the ids to the callers
queue_matchId = CachedInQueue()
queue_accountId = CachedInQueue()

# Plug the match parser to the match caller
match.set_callback(match_parser.parse)
# Plug the matchlist parser to the matchlist caller
matchlist.set_callback(matchlist_parser.parse)

# Give to the callers a queue to get the ids the call
match.set_input_queue(queue_matchId)
matchlist.set_input_queue(queue_accountId)

# Give to the parser a queue to send the extracted ids to
match_parser.set_output_queue(queue_accountId)
matchlist_parser.set_output_queue(queue_matchId)

# A seeder to bootstrap the crawler
seeder = AccountIdSeeder()
seeder.set_output_queue(queue_accountId)

# Put everything in Targon
targon = Targon([
    match,
    matchlist,
    match_parser,
    matchlist_parser,
    queue_matchId,
    queue_accountId,
    seeder
])