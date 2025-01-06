from lxml import etree

from ttxfont import Simulator
from ttxread import read_ttx

def test_read_simulate_tokens(filename, tokens):
    font = read_ttx(filename)
    sim = Simulator(font)
    sim.suppressed = ['ss01', 'rtlm']
    sim.set_tokens(tokens)
    print(sim.in_tokens_str() + '\n')
    print(sim.steps_str(), end='')
    print(sim.shaped_str())

def test_read_simulate_string(filename, string):
    font = read_ttx(filename)
    sim = Simulator(font)
    sim.suppressed = ['ss01', 'rtlm']
    sim.set_string(string)
    print(sim.in_tokens_str() + '\n')
    print(sim.steps_str(), end='')
    print(sim.shaped_str())

# Two possible uses:

# (1) With characters
test_read_simulate_string('myfont.ttx', '+*')

# (2) With names of characters
test_read_simulate_tokens('myfont.ttx', ['plus', 'asterisk'])
