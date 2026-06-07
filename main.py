import functions
import json
import numpy as np
import re

if __name__ == "__main__":
    with open('game_masters/latest/latest.json') as f:
        master = json.load(f)
    with open('have.json') as g:
        current = json.load(g)

    # Pre-index 'have.json' data for O(1) lookups
    # Structure: { "PIKACHU": [entry1, entry2], ... }
    pokemon_lookup = {}
    for x in current['pokemon']:
        name = x['name'].upper()
        if name not in pokemon_lookup:
            pokemon_lookup[name] = []
        pokemon_lookup[name].append(x)

    # load_from_data(data)
    multiplier = []
    functions.populate_multiplier(master, multiplier)
    base_ivs = [0, 0, 0]
    ivs = [-1, -1, -1]
    form = ""
    evolutions = set()
    dtype = [('A', np.int32), ('D', np.int32), ('S', np.int32), ('cp', np.int32), ('form', 'U10')]

    while True:

        entry = input('Pokemon name, type q to exit: ')
        # print(entry)
        if entry == 'q':
            break

        entries = entry.split()
        # print(len(entries))
        if len(entries) != 3:
            evolutions.clear()
            functions.populate_evolutions(master, evolutions, entries[0])
            ivs = [-1, -1, -1]
            if len(entries) != 1:
                form = entries[1]
            else:
                form = ""
        else:
            for i in range(0, 3):
                ivs[i] = int(entries[i])

        for species in evolutions:
            print(species)
            functions.populate_ads(master, species, base_ivs)

            # Use the pre-indexed lookup and collect in a list instead of np.append
            temp_data_list = []
            species_matches = pokemon_lookup.get(species.upper(), [])
            
            for x in species_matches:
                x_form = x.get('form', "")
                # Match if form matches or if no form is specified and entry has no form
                if (form and x_form == form) or (not form and not x_form):
                    temp_data_list.append((
                        x['stats']['ivAttack'],
                        x['stats']['ivDefense'],
                        x['stats']['ivStamina'],
                        x['league'],
                        x_form if x_form else "      "
                    ))
            
            structuredArr = np.array(temp_data_list, dtype=dtype)

            for data in structuredArr:

                # in if branch, we are showing what we have
                if -1 == ivs[0]:
                    # get all combinations better or equal to current IVs
                    all_levels = functions.get_all_levels(base_ivs[0], base_ivs[1], base_ivs[2], data['A'], data['D'],
                                                          data['S'], multiplier, data['cp'])
                    max_a = 0
                    min_d = 15
                    min_s = 15
                    for i in all_levels:
                        max_a = max(max_a, i[0])
                        min_d = min(min_d, i[1])
                        min_s = min(min_s, i[2])
                    print(data['cp'], data['form'], ":", max_a, min_d, min_s, "#", all_levels.size)
                else:
                    all_levels_size = functions.get_num_levels(base_ivs[0], base_ivs[1], base_ivs[2], data['A'],
                                                               data['D'], data['S'], multiplier, data['cp'])
                    newRank = functions.get_all_levels(base_ivs[0], base_ivs[1], base_ivs[2], ivs[0], ivs[1],
                                                       ivs[2], multiplier, data['cp'])
                    if newRank.size < all_levels_size:
                        print(data['cp'], data['form'], ":", ivs[0], ivs[1], ivs[2], 'L'+str(newRank[-1][4]),
                              '#'+str(newRank.size))
