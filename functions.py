import math
import numpy as np

def quadratic_mean(a,b):
    return math.sqrt((a*a+b*b)/2.0)

def populate_multiplier(data,multiplier):
    for i in data:
        if i['templateId'] == 'PLAYER_LEVEL_SETTINGS':
            cpList = i['data']['playerLevel']['cpMultiplier']
    #multiplier.extend(cpList)
    for i in range(len(cpList)-1):
        #from level 1 to 44
        #first append level
        multiplier.append(cpList[i])
        #calculate half level
        multiplier.append(quadratic_mean(cpList[i],cpList[i+1]))
    multiplier.append(cpList[-1])

def populate_evolutions(data,evolutions,name):
    #find all related pokemon. will take multiple passes
    evolutions.add(name.upper())
    pre_size=0
    while(pre_size != len(evolutions)):
        pre_size = len(evolutions)
        for i in data:
            if (i['templateId'].find('_POKEMON_')!=-1) & i['templateId'].startswith('V0'):
                if 'pokemonSettings' in i['data']:
                    if i['data']['pokemonSettings']['pokemonId'] in evolutions:
                        if 'parentPokemonId' in i['data']['pokemonSettings']:
                            evolutions.add(i['data']['pokemonSettings']['parentPokemonId'])
                        if 'evolutionBranch' in i['data']['pokemonSettings']:
                            for j in i['data']['pokemonSettings']['evolutionBranch']:
                                if 'evolution' in j:
                                    evolutions.add(j['evolution'])
                    elif 'form' in i['data']['pokemonSettings']:        #whole elif for Pumpkaboos, some Alolans (Sandshrew)
                        if i['data']['pokemonSettings']['form'] in evolutions:
                            if 'evolutionBranch' in i['data']['pokemonSettings']:
                                for j in i['data']['pokemonSettings']['evolutionBranch']:
                                    if 'form' in j:
                                        evolutions.add(j['form'])
            elif (i['templateId'].find('_POKEMON_')!=-1) & i['templateId'].startswith('EVOLUTION_V0'):
                if 'obEvolutionChainDisplaySettings' in i['data']:
                    if i['data']['obEvolutionChainDisplaySettings']['pokemon'] in evolutions:
                        if 'obChain' in i['data']['obEvolutionChainDisplaySettings']:
                            for j in i['data']['obEvolutionChainDisplaySettings']['obChain']:
                                if 'obEvolutionChainEntry' in j:
                                    for k in j['obEvolutionChainEntry']:
                                        if 'pokemon' in k:
                                            evolutions.add(k['pokemon'])
                                        if 'form' in k:
                                            if not k['form'].endswith('NORMAL'):
                                                evolutions.add(k['form'])


def populate_ads(data,name,ivs):
    for i in data:
        if i['templateId'].endswith("POKEMON_" + name.upper()) & i['templateId'].startswith("V0"):
            ivs[0] = i['data']['pokemonSettings']['stats']['baseAttack']
            ivs[1] = i['data']['pokemonSettings']['stats']['baseDefense']
            ivs[2] = i['data']['pokemonSettings']['stats']['baseStamina']

def level_from_index(index):
    #0->1, 1->1.5, 2->2, 3->2.5, 4->3
    return (index+2.0)/2.0

def get_cp(a,d,s,multiplier,inx):
    return math.floor((a * math.sqrt(d) * math.sqrt(s) * multiplier[inx] * multiplier[inx] ) / 10.0)

def get_level(a,d,s,multiplier,maxCP=80000):
    level = 0.5
    cp = 1
    inx = -1
    while(cp <= maxCP and level < 50.5):
        inx += 1
        level+=0.5
        cp = get_cp(a,d,s,multiplier,inx)
    return level - 0.5

def get_index(a,d,s,multiplier,maxCP=80000):
    cp = 1
    inx = -1
    while(cp <= maxCP and inx < 99):
        inx += 1
        cp = get_cp(a,d,s,multiplier,inx)
    return inx-1

def load_from_data(data):
    for i in data['template']:
        if '_NORMAL' not in i['templateId'] and\
                '_SHADOW' not in i['templateId'] and\
                '_PURIFIED' not in i['templateId']:
            if 'pokemon' in i:
                print(i['pokemon']['uniqueId'])

def get_prodcut(a,d,s,iv_a,iv_d,iv_s,mult):
    return (a+iv_a)*mult*(d+iv_d)*mult*math.floor((s+iv_s)*mult)

def get_all_levels(a,d,s,iv_a,iv_d,iv_s,multiplier,maxCP=80000):
    dtype = [('A', np.int32), ('D', np.int32), ('S', np.int32), ('product', np.float64), ('level', np.float64)]
    structuredArr = np.array([],dtype=dtype)

    mult_idx = get_index(a + iv_a, d + iv_d, s + iv_s, multiplier, maxCP)
    min_product = get_prodcut(a,d,s,iv_a,iv_d,iv_s,multiplier[mult_idx])

    for a_iv in range(16):
        for d_iv in range(16):
            for s_iv in range(16):
                mult_idx = get_index(a+a_iv,d+d_iv,s+s_iv,multiplier,maxCP)
                product = get_prodcut(a, d, s, a_iv, d_iv, s_iv, multiplier[mult_idx])
                if(product >= min_product):
                    structuredArr = np.append(structuredArr, np.array([(a_iv,d_iv,s_iv,product,level_from_index(mult_idx))],structuredArr.dtype))
    structuredArr.sort(order='product')
    structuredArr = np.flip(structuredArr)
    return structuredArr

#get all levels, but only returns the count
def get_num_levels(a,d,s,iv_a,iv_d,iv_s,multiplier,maxCP=80000):
    retval=0
    mult_idx = get_index(a + iv_a, d + iv_d, s + iv_s, multiplier, maxCP)
    min_product = get_prodcut(a,d,s,iv_a,iv_d,iv_s,multiplier[mult_idx])

    for a_iv in range(16):
        for d_iv in range(16):
            for s_iv in range(16):
                mult_idx = get_index(a+a_iv,d+d_iv,s+s_iv,multiplier,maxCP)
                product = get_prodcut(a, d, s, a_iv, d_iv, s_iv, multiplier[mult_idx])
                if(product >= min_product):
                    retval+=1
    return retval
