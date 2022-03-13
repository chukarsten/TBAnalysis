import pandas as pd
import numpy as np
from unitids import unitids

desired_width = 320
pd.set_option('display.width', desired_width)
np.set_printoptions(linewidth=desired_width)
pd.set_option('display.max_columns', 20)

guild_data = pd.read_csv("March LSGEO/BRG Order of the EbonHand.csv").rename(columns={"Name": "name"}).set_index("name")
guild_data["TotalGP"] = guild_data["CharacterGP"] + guild_data["ShipGP"]
guild_data_with_roster = pd.read_csv("March LSGEO/BRG Order of the EbonHandFull.csv").rename(columns={"Name": "name"}).set_index(
	"name")
guild_data_with_roster = guild_data_with_roster[guild_data_with_roster.index != "Glowganja"]
total = pd.read_csv("March LSGEO/LSGEO MAR Total.csv")
total = total.rename(columns={"Name": "name"})
total = total.set_index("name")
p1 = pd.read_csv("March LSGEO/LSGEO MAR P1.csv", index_col="name").add_suffix("_phase1")
p2 = pd.read_csv("March LSGEO/LSGEO MAR P2.csv", index_col="name").add_suffix("_phase2")
p3 = pd.read_csv("March LSGEO/LSGEO MAR P3.csv", index_col="name").add_suffix("_phase3")
p4 = pd.read_csv("March LSGEO/LSGEO MAR P4.csv", index_col="name").add_suffix("_phase4")

from functools import reduce

df_final = reduce(lambda left, right: pd.merge(left, right, on='name'), [p1, p2, p3, p4])

# Undeployed Character Analysis
undeployed_characters = df_final[[f"minEstimatedCombatDeploymentRemaining_phase{i}" for i in range(1, 5)]]
rename_dict = {f"minEstimatedCombatDeploymentRemaining_phase{i}": f"phase{i}" for i in range(1, 5)}
undeployed_characters = undeployed_characters.rename(columns=rename_dict)
undeployed_characters["total(millions)"] = undeployed_characters.sum(axis=1) / 1000000
offenders = undeployed_characters[undeployed_characters["total(millions)"] != 0].sort_values("total(millions)",
                                                                                             ascending=False)

# Mission Attempts Analysis
rename_dict = {f"Mission Attempts Phase {i}": f"Att P{i}" for i in range(1, 5)}
rename_dict.update({f"Mission Waves Phase {i}": f"Wvs P{i}" for i in range(1, 5)})
attempted_missions = total[
	[f"Mission Attempts Phase {i}" for i in range(1, 5)] + [f"Mission Waves Phase {i}" for i in range(1, 5)]].fillna(0)
attempted_missions["Att Total"] = attempted_missions.sum(axis=1)
attempted_missions["Wvs Total"] = attempted_missions.sum(axis=1)
attempted_missions = attempted_missions.astype(int)
attempted_missions = pd.merge(attempted_missions, guild_data[["TotalGP"]], on="name")
attempted_missions = attempted_missions.rename(columns=rename_dict)


# Searching for a unit
def get_unitid(search_term):
	return [x for x in unitids if search_term in x]


def get_player_with_unit(unitid):
	unitid = unitid.upper()
	if unitid not in unitids:
		print(unitid + " is close to " + str(get_unitid(unitid)))
	else:
		return guild_data_with_roster[guild_data_with_roster["BaseId"] == unitid][
			["GearLevel", "Power", "ZetaCount", "Ultimate"]].sort_values("Power")


def build_unit_str(unitid):
	character_frame = get_player_with_unit(unitid).astype(str)
	character_frame[unitid] = [f"z{c}/g{a}/{b} GP/Ult {d}" for a, b, c, d in
	                           zip(character_frame['GearLevel'], character_frame['Power'], character_frame['ZetaCount'],
	                               character_frame['Ultimate'])]
	return character_frame[unitid]


for unitid in ["GRANDMASTERLUKE", "JEDIMASTERKENOBI", "GLREY", "JEDIKNIGHTLUKE"]:
	attempted_missions = attempted_missions.merge(build_unit_str(unitid), on="name", how="outer")
attempted_missions = attempted_missions.fillna(value="None")
attempted_missions["Att Total"] = attempted_missions["Att Total"].astype(int)
attempted_missions = attempted_missions.sort_values("Att Total")
attempted_missions = attempted_missions.drop([attempted_missions.columns[i] for i in range(8)],
                                             axis=1)  # Remove the by phase info
print(attempted_missions)

four_wave_mission_regex = "P\d\s\w*\s\d*_\d*_\d*_\d*\s\[\d\]"
ground_cm_columns = [x for x in total.columns if "P1 Ground" in x]
fleet_cm_columns = [x for x in total.columns if "Fleet" in x]
ground_cm_results = total[ground_cm_columns]
fleet_cm_results = total[fleet_cm_columns]
breakpoint()