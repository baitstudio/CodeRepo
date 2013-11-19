import nuke

#creating the Glapp menu
menubar = nuke.menu("Nuke")
m = menubar.addMenu("BAIT")

#mocha to nuke
nuke.menu('Nuke').addCommand('BAIT/MochaToNuke','import Mocha_AE_Import_v01 as mton;mton.Mocha_AE_Import()')

#deadline
import DeadlineNukeClient
menubar = nuke.menu("Nuke")
tbmenu = menubar.addMenu("&Thinkbox")
tbmenu.addCommand("Submit Nuke To Deadline", DeadlineNukeClient.main, "")