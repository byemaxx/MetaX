# Function: extract the taxonomic level and COG of each protein group
# Input: a list of protein names (e.g. ['MGYG00000001_1', 'MGYG000000
# Output: a list of taxonomic levels and annotations of each protein group
# Author: Qing Wu
# 
# Date: 2023-01-17
# Version:0.2.1
# Update: change cog to eggNOG_OGs, COG_category, Description,Preferred_name, GOs, KEGG_ko, KEGG_Pathway, PFAMs  
# and return they proportion of each annotation
#
# Date: 2023-02-16
# Version:0.2.2
# Change out format to a dict
#
# Date: 2023-03-23
# Version:0.2.3
# Change NULL to unknown
#
# Date: 2023-04-19
# Version:0.2.4
# Change taxa level output from (d, p, c, o, f, g, s) to (domain, phylum, class, order, family, genus, species)
# l(life): when the taxa level is cannot define at domain level,e.g.  d_Archaea and  d_Bacteria both present, return l
#
# Date: 2023-05-08
# Version:0.2.5
# Add function annotation: 
# 
# Date: 2023-06-13
# Version:0.2.6
# Test if the MGYG did not annotate to species level. Everytthing is ok.
#
# Date: 2023-07-10
# Version:0.2.7
# change the way to extract the function annotation, extract all except the specific column


from collections import Counter
import sqlite3

# open the database of eggNOG animation of MGYG and return the connection
def open_eggnog_db(db_path):
    conn = sqlite3.connect(db_path)
    conn.cursor()
    return conn

# return a list of taxonomic levels of each protein
def query_taxon_from_db(conn, protein_list):
    c = conn.cursor()
    taxa = []
    sql = 'SELECT Lineage from mgyg2taxon where Species_rep = ?'
    for i in protein_list:
        i = i.split('_')[0]
        if re := c.execute(sql, (i,)).fetchone():
            taxa.append(re[0])
        else:
            #taxon_level.append('d__NULL;p__NULL;c__NULL;o__NULL;f__NULL;g__NULL;s__NULL')
            taxa.append('unknown')

    return taxa



# return the last common ancestor and its percentage         
def find_LCA(taxa_list: list, threshold: float =1.0):
    # split the taxon level by semicolon for each element in the list
    taxa_list = [tax.split(';') for tax in taxa_list]
    taxa_level_dict = {'d': 'domain', 'p': 'phylum', 'c': 'class',
                       'o': 'order', 'f': 'family', 'g': 'genus', 's': 'species'}

    tax_re = None
    # '6543210' present the location of the taxon level in the list(s to d)
    for j in range(6, -1, -1):
        # join the taxon level by the level number
        taxa_level_list = [str.join('|', k[:int(j)+1]) for k in taxa_list]

        most = Counter(taxa_level_list).most_common(1)
        proportion = most[0][1] / len(taxa_level_list)
        tax = most[0][0]
        if tax == 'unknown':
            tax_re = 'unknown', tax, proportion

        elif proportion >= float(threshold) and tax.split('__')[-1] != '':
            lca_level = taxa_level_dict[tax.split('|')[-1].split('__')[0]]
            tax_re = lca_level, tax, proportion
            break
        elif j == 0 and tax_re is None:
            # when taxa level move to domain and still not found, return 'l' means 'life'
            tax_re = 'life', tax, proportion

    return tax_re
         
# return a dict of anatation of each protein
def query_protein_from_db(conn, protein_list):
    c = conn.cursor()
    # get all columns name
    c.execute('select * from mgyg2eggnog')
    col_name = [tuple[0] for tuple in c.description]
    # remove the columns that not need
    for i in ['query', 'seed_ortholog', 'evalue', 'score']:
        if i in col_name:
            col_name.remove(i)
   
    sql = 'SELECT ' + ','.join(col_name) + ' from mgyg2eggnog where query = ?'
    re_dict = {i: [] for i in col_name}
    
    for i in protein_list:
        re = c.execute(sql, (i,)).fetchone()
        if re is not None:
            for j in range(len(re)):
                func = re[j]
                if func not in ['', '-']:
                    re_dict[list(re_dict.keys())[j]].append(func)
                else:
                    re_dict[list(re_dict.keys())[j]].append('unknown')

        else:
            for v in re_dict.values():
                # if the protein is not found in the database, return 'unknown'
                v.append('unknown')

    return re_dict




# find the most common annotation and its percentage
def stats_fun(re_dict):
    for i in re_dict:
        re_dict[i] = Counter(re_dict[i]).most_common(1)[0][0], Counter(re_dict[i]).most_common(1)[0][1]/len(re_dict[i])
    return re_dict

# return a dict of taxonomic level and annotation and their percentage    
def create_dict_out(function_results, taxa_results):
    taxa_level, taxa, taxa_prop = taxa_results[0], taxa_results[1], round(taxa_results[2], ndigits=4)
    re_out = {'LCA_level': taxa_level, 'Taxon': taxa, 'Taxon_prop': taxa_prop}
    for function, (result, proportion) in function_results.items():
        re_out[function] = result
        re_out[f'{function}_prop'] = proportion
    return re_out

    
def proteins_to_taxa_func(protein_list: list,  db_path: str, threshold = 1.0 ) -> dict:
    conn = open_eggnog_db(db_path)

    re_dict = query_protein_from_db(conn, protein_list)

    fun_re = stats_fun(re_dict)

    taxa_list = query_taxon_from_db(conn, protein_list)

    taxa_re = find_LCA(taxa_list, threshold)

    return create_dict_out(fun_re, taxa_re)


# ### test data

pep0 = 'sp|Q9Y6J9|TAF6L_HUMAN;MGYG000003922_02341;MGYG000002528_00252;MGYG000003013_00743;MGYG000000216_03651;MGYG000000842_01470;MGYG000000321_01351;MGYG000004797_00839;MGYG000001531_01450;MGYG000003427_02815;MGYG000000482_00745;MGYG000000036_00577;MGYG000002033_00922;MGYG000002829_00401;MGYG000003063_02160;MGYG000002310_01930;MGYG000001606_00355;MGYG000000245_03557;MGYG000004112_00055;MGYG000000584_01041;MGYG000004885_01359;MGYG000000236_03127;MGYG000001616_01766;MGYG000003381_01965;MGYG000002963_02976;MGYG000003992_01347;MGYG000003063_00913;MGYG000004885_00440;MGYG000004719_01113;MGYG000002528_02623;MGYG000003381_01906;MGYG000002963_02454;MGYG000004573_01964;MGYG000002445_01680;MGYG000002963_04470;MGYG000001502_02461;MGYG000001346_01678;MGYG000004716_00540;MGYG000001338_01117;MGYG000002136_02243;MGYG000004834_00110;MGYG000000080_03070;MGYG000001920_00058;MGYG000002560_01716;MGYG000000482_00494;MGYG000001655_02939;MGYG000002963_02368;MGYG000004215_00828;MGYG000000842_00884;MGYG000003427_00456;MGYG000004747_01462;MGYG000002310_08060;MGYG000001456.1_00641;MGYG000001646_01154;MGYG000002910_00828;sp|Q8N1T3|MYO1H_HUMAN;MGYG000000403_00561;MGYG000001531_00265;MGYG000000045_02648;MGYG000001482_02397;MGYG000000193_03109;MGYG000002023_00706;MGYG000001315_00779;MGYG000001606_01101;MGYG000000792_00618;MGYG000001032_00530;MGYG000001493_02537;MGYG000002930_00273;MGYG000001643_01086;MGYG000003539_01229;MGYG000004797_02729;MGYG000003013_01489;MGYG000004573_01468;MGYG000003351_00312;MGYG000002560_02514;MGYG000003116_00329;MGYG000000408_00430;MGYG000000074_02532;MGYG000004402_02126;MGYG000004462_01749;MGYG000002591_00013;MGYG000002613_00690;MGYG000003681_02964;sp|P78371|TCPB_HUMAN;MGYG000002290_00657;MGYG000003922_02722;MGYG000002101_01854;MGYG000000584_02124;MGYG000001315_00523;sp|P00505|AATM_HUMAN;MGYG000001424_00577;MGYG000002829_02297;sp|Q8N4B4|FBX39_HUMAN'
pep1 = 'MGYG000001461_01153' 
pep4 = 'sp|Q9Y6J9|TAF6L_HUMAN'
pep3 = 'MGYG000001461_01153;MGYG000001433_02665;MGYG000000692_01998;MGYG000002218_01282;MGYG000002613_01391;MGYG000003362_01893;MGYG000001489_05093;MGYG000003701_03025;MGYG000003572_01499;MGYG000004703_00856;MGYG000003922_03504;MGYG000001306_02283;MGYG000002171_02951;MGYG000001370_01800;MGYG000003521_01703;MGYG000001661_02454;MGYG000003681_02380;MGYG000004876_03429;MGYG000002478_02348;MGYG000002560_01922;MGYG000004462_01892;MGYG000002033_02341;MGYG000004573_00155;MGYG000003351_04015;MGYG000000701_00512;MGYG000002803_01060;MGYG000002905_00355;MGYG000001789_01041;MGYG000000044_02493;MGYG000003992_01037;MGYG000001345_00123;MGYG000001920_00259;MGYG000002930_01172;MGYG000004479_00136;MGYG000004638_00481;MGYG000002721_01600;MGYG000001795_01566;MGYG000001447_02134;MGYG000000781_01187;MGYG000003553_01246;MGYG000004763_00292;MGYG000000105_02793;MGYG000000273_02278;MGYG000001783_02036;MGYG000001042_00610;MGYG000001925_01551;MGYG000002064_01248;MGYG000000923_01112;MGYG000002209_00490;MGYG000001735_00719;MGYG000001346_01263;MGYG000002300_02398;MGYG000001337_03571;MGYG000001874_01633;MGYG000000355_00237;MGYG000002205_01064;MGYG000001835_02078;MGYG000000098_02845;MGYG000004464_01125'
pep2 = 'MGYG000003142_01865;MGYG000002451_01541;MGYG000000196_03974;MGYG000004573_00004;MGYG000004383_01197;MGYG000004885_00596;MGYG000003380_01904;MGYG000001661_02666;MGYG000001638_00325;MGYG000001977_02434;MGYG000004407_00565;MGYG000003424_00456;MGYG000003155_00314;MGYG000000273_00431;MGYG000000236_01807;MGYG000003681_02037;MGYG000002560_00219;MGYG000004654_00761;MGYG000001787_01812;MGYG000003185_01053;MGYG000001140_00952;MGYG000003185_01074;MGYG000003361_00615;MGYG000001337_03907;MGYG000003992_01709;MGYG000003142_01879;MGYG000004681_01647;MGYG000002528_01098;MGYG000004294_00528;MGYG000000036_01380;MGYG000002023_01111;MGYG000001346_01533;MGYG000002132_01420;MGYG000002455_03884;MGYG000002910_01409;MGYG000004608_01611;MGYG000004602_01203;MGYG000003514_00785;MGYG000002766_00990;MGYG000002754_00615'
pep7 = 'MGYG000004446_00495;sp|A2VDJ0|T131L_HUMAN'
pep8 = 'MGYG000001672_00307;MGYG000000076_00845;MGYG000001247_02013;MGYG000004707_01591;MGYG000003390_00543;sp|Q9BQP9|BPIA3_HUMAN;MGYG000001776_00424;sp|Q15031|SYLM_HUMAN'
pep9 = 'MGYG000004876_02622'
pep10 = 'MGYG000002766_00930;MGYG000002754_01086;MGYG000004681_00317'
pep11 = 'MGYG000002864_01541;MGYG000004383_00684;MGYG000004407_01207;MGYG000002754_01423;MGYG000002766_01563;MGYG000001140_00858;MGYG000001176_00975;MGYG000004294_01434'
pep_null = 'MGYG000000137_01815;MGYG000001639_01406;MGYG000000236_03945'
pep_no_species_level = "MGYG000000385;MGYG000002077;MGYG000003829"
### test data

if __name__ == '__main__':
    import time
    t1 = time.time()
    
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = 'C:/Users/Qing/Desktop/New Folder/MetaX-human-gut_new.db'
    # db_path = os.path.join(current_dir, r'TaxaFuncExplore_database\TaxaFuncExplore.db')
    print(db_path)

    
    for i in [pep_no_species_level, pep_null, pep2, pep7, pep8, pep9, pep10, pep11]:
        print(i)
        protein_list = i.split(';')
        # re = proteins_to_taxa_func(protein_list, threshold = 1, db_path='C:/Projects/pep2func/mgyg2eggnog.db')
        re = proteins_to_taxa_func(protein_list, threshold = 1, db_path=db_path)
        keys = list(re.keys())
        for i in range(len(keys)):
            key = keys[i]
            value = re[key]
            print("{:<20}{}".format(key, value))
        print('\n\n')
    
    t2 = time.time()
    print(f'Time: {t2-t1}')