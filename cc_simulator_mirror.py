"""
Cookie Clicker Simulator
"""

import simpleplot
import math

# Used to increase the timeout, if necessary
import codeskulptor
codeskulptor.set_timeout(20)

import poc_clicker_provided as provided

# Constants
SIM_TIME = 10000000000.0

class ClickerState:
    """
    Simple class to keep track of the game state.
    """
    
    def __init__(self):
        self._total_cookies = 0.0
        self._current_cookies = 0.0
        self._current_time = 0.0
        self._cps = 1.0
        self._history = [(0.0, None, 0.0, 0.0)]
        
    def __str__(self):
        """
        Return human readable state
        """
        readable = ""
        readable += "Total cookies generated thus far: "
        readable += str(self._total_cookies)
        readable += "\nCurrent number of cookies: "
        readable += str(self._current_cookies)
        readable += "\nTime elapsed: "
        readable += str(self._current_time)
        readable += "\nCPS: "
        readable += str(self._cps)
        return readable
        
    def get_cookies(self):
        """
        Return current number of cookies 
        (not total number of cookies)
        
        Should return a float
        """
        return self._current_cookies
    
    def get_cps(self):
        """
        Get current CPS

        Should return a float
        """
        return self._cps
    
    def get_time(self):
        """
        Get current time

        Should return a float
        """
        return self._current_time
    
    def get_history(self):
        """
        Return history list

        History list should be a list of tuples of the form:
        (time, item, cost of item, total cookies)

        For example: [(0.0, None, 0.0, 0.0)]

        Should return a copy of any internal data structures,
        so that they will not be modified outside of the class.
        """
        return list(self._history)

    def time_until(self, cookies):
        """
        Return time until you have the given number of cookies
        (could be 0.0 if you already have enough cookies)

        Should return a float with no fractional part
        """
        cookie_difference = float(cookies - self._current_cookies)
        if cookie_difference > 0:
            time_difference = math.ceil(cookie_difference / self._cps)
            return time_difference
        else:
            return 0.0
    
    def wait(self, time):
        """
        Wait for given amount of time and update state

        Should do nothing if time <= 0.0
        """
        if time > 0.0:
            self._total_cookies += (self._cps * time)
            self._current_cookies += (self._cps * time)
            self._current_time += time
        else:
            return
    
    def buy_item(self, item_name, cost, additional_cps):
        """
        Buy an item and update state

        Should do nothing if you cannot afford the item
        """
        if self._current_cookies >= cost:
            self._current_cookies -= cost
            self._cps += additional_cps
            self._history.append((self._current_time, item_name, cost, self._total_cookies))
        else:
            return
               
    
def simulate_clicker(build_info, duration, strategy):
    """
    Function to run a Cookie Clicker game for the given
    duration with the given strategy.  Returns a ClickerState
    object corresponding to the final state of the game.
    """
    structure = build_info.clone()
    game = ClickerState()
    while game.get_time() <= duration:
        time_remaining = duration - game.get_time()
        item_to_buy = strategy(game.get_cookies(), game.get_cps(), 
                               game.get_history(), time_remaining, structure)
        if item_to_buy == None:
            break
        item_cost = structure.get_cost(item_to_buy)
        time_to_wait = game.time_until(item_cost)
        if time_to_wait > time_remaining:
            break
        game.wait(time_to_wait)
        game.buy_item(item_to_buy, item_cost, structure.get_cps(item_to_buy))
        structure.update_item(item_to_buy)
    game.wait(time_remaining)
    return game


def strategy_cursor_broken(cookies, cps, history, time_left, build_info):
    """
    Always pick Cursor!

    Note that this simplistic (and broken) strategy does not properly
    check whether it can actually buy a Cursor in the time left.  Your
    simulate_clicker function must be able to deal with such broken
    strategies.  Further, your strategy functions must correctly check
    if you can buy the item in the time left and return None if you
    can't.
    """
    return "Cursor"

def strategy_none(cookies, cps, history, time_left, build_info):
    """
    Always return None

    This is a pointless strategy that will never buy anything, but
    that you can use to help debug your simulate_clicker function.
    """
    return None

def strategy_cheap(cookies, cps, history, time_left, build_info):
    """
    Always buy the cheapest item you can afford in the time left.
    """    
    item_list = build_info.build_items()
    item_cost_list = map(build_info.get_cost, item_list)
    cheapest_cost = min(item_cost_list)
    maximum_cookies_accumulatable = cookies + cps * time_left
    #If the number of cookies you require for the cheapest item
    #Is greater than the number of cookies you can accumulate
    #You can't buy anything
    if cheapest_cost > maximum_cookies_accumulatable:
        return None
    else:
        return item_list[item_cost_list.index(cheapest_cost)]

def strategy_expensive(cookies, cps, history, time_left, build_info):
    """
    Always buy the most expensive item you can afford in the time left.
    """
    item_list = build_info.build_items()
    item_cost_list = map(build_info.get_cost, item_list)
    maximum_cookies_accumulatable = cookies + cps * time_left
    least_difference = float('inf')
    to_buy = None
    #In essence, the most expensive item given the time left is the purchase
    #Which leaves you with the least number of remaining cookies
    for cost in item_cost_list:
        difference = maximum_cookies_accumulatable - cost
        if 0 <= difference < least_difference:
            least_difference = difference
            to_buy = item_list[item_cost_list.index(cost)]
    return to_buy

def strategy_best(cookies, cps, history, time_left, build_info):
    """
    The best strategy that you are able to implement.
    Here I will try for the cost-effective approach.
    """
    #As always, find the maximum number of cookies we can possibly get for a given cps
    maximum_cookies_accumulatable = cookies + cps * time_left
    #We begin by generating lists of cost and cps
    item_list = build_info.build_items()
    item_cost_list = map(build_info.get_cost, item_list)
    item_cps_list = map(build_info.get_cps, item_list)
    greatest_cost_effectiveness = float('-inf')
    best_recommendation = None
    #Then we ask, which item (that we can afford) gives us the biggest cps boost for the smallest cost?
    for cps in item_cps_list:
        corr_cost = item_cost_list[item_cps_list.index(cps)]
        cost_effectiveness = float(cps / corr_cost)
        if corr_cost <= maximum_cookies_accumulatable:
            if cost_effectiveness > greatest_cost_effectiveness:
                greatest_cost_effectiveness = cost_effectiveness
                best_recommendation = item_list[item_cps_list.index(cps)]
    return best_recommendation
           
def run_strategy(strategy_name, time, strategy):
    """
    Run a simulation for the given time with one strategy.
    """
    state = simulate_clicker(provided.BuildInfo(), time, strategy)
    print strategy_name, ":", state

    # Plot total cookies over time

    # Uncomment out the lines below to see a plot of total cookies vs. time
    # Be sure to allow popups, if you do want to see it

#    history = state.get_history()
#    history = [(item[0], item[3]) for item in history]
#    simpleplot.plot_lines(strategy_name, 1000, 400, 'Time', 'Total Cookies', [history], True)

def run():
    """
    Run the simulator.
    """    
    # run_strategy("Cursor", SIM_TIME, strategy_cursor_broken)

    # Add calls to run_strategy to run additional strategies
    # run_strategy("Cheap", SIM_TIME, strategy_cheap)
    # run_strategy("Expensive", SIM_TIME, strategy_expensive)
    # run_strategy("Best", SIM_TIME, strategy_best)
    
run()    
