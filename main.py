import os
from copy import deepcopy

def creer_automate():
    return {
        "nom"           : "",
        "nb_symboles"   : 0,
        "alphabet"      : [],
        "nb_etats"      : 0,
        "etats"         : [],
        "initiaux"      : [],
        "terminaux"     : [],
        "nb_transitions": 0,
        "transitions"   : [],
    }

def copier_automate(af):
    return deepcopy(af)

#  LECTURE D'UN AUTOMATE DEPUIS UN FICHIER

def lire_automate(chemin_fichier):
    if not os.path.exists(chemin_fichier):
        print(f"  ERREUR : fichier '{chemin_fichier}' introuvable.")
        return None

    with open(chemin_fichier, 'r', encoding='utf-8') as f:
        lignes = [l.strip() for l in f if l.strip()]

    af = creer_automate()
    af["nom"] = os.path.splitext(os.path.basename(chemin_fichier))[0]
    idx = 0

    af["nb_symboles"] = int(lignes[idx]); idx += 1
    af["alphabet"]    = [chr(ord('a') + i) for i in range(af["nb_symboles"])]

    af["nb_etats"] = int(lignes[idx]); idx += 1
    af["etats"]    = list(range(af["nb_etats"]))

    # CORRECTION ICI : On ignore le premier chiffre (qui est la quantité)
    valeurs_init = [int(x) for x in lignes[idx].split()]
    af["initiaux"] = valeurs_init[1:] if len(valeurs_init) > 0 else []
    idx += 1

    # CORRECTION ICI : On ignore le premier chiffre (qui est la quantité)
    valeurs_term = [int(x) for x in lignes[idx].split()]
    af["terminaux"] = valeurs_term[1:] if len(valeurs_term) > 0 else []
    idx += 1

    af["nb_transitions"] = int(lignes[idx]); idx += 1

    af["transitions"] = []
    for i in range(af["nb_transitions"]):
        if idx + i >= len(lignes):
            break
        t_str = lignes[idx + i]
        for j, char in enumerate(t_str):
            if char.isalpha():
                dep = int(t_str[:j])
                sym = char
                arr = int(t_str[j + 1:])
                af["transitions"].append((dep, sym, arr))
                break

    return af

#  AFFICHAGE DE L'AUTOMATE

def afficher_automate(af, titre=None):
    sep = "=" * 60
    print(sep)
    print(f"  {titre if titre else 'Automate : ' + af['nom']}")
    print(sep)
    print(f"  Alphabet   : {{ {', '.join(af['alphabet'])} }}")
    print(f"  États      : {{ {', '.join(str(e) for e in af['etats'])} }}")
    print(f"  Initiaux   : {{ {', '.join(str(e) for e in af['initiaux'])} }}")
    print(f"  Terminaux  : {{ {', '.join(str(e) for e in af['terminaux'])} }}")
    print(f"  Transitions: {af['nb_transitions']}")
    print()

    table = {e: {s: [] for s in af["alphabet"]} for e in af["etats"]}
    for (dep, sym, arr) in af["transitions"]:
        if sym in table.get(dep, {}):
            table[dep][sym].append(arr)

    col_w = max(6, max((len(str(e)) for e in af["etats"]), default=1) + 4)
    sym_w = [
        max(len(s), max((len(','.join(str(x) for x in table[e][s])) for e in af["etats"]), default=0) + 1)
        for s in af["alphabet"]
    ]
    sym_w = [max(w, 4) for w in sym_w]

    header = f"  {'':4}{'État':>{col_w}}"
    for i, s in enumerate(af["alphabet"]):
        header += f"  {s:^{sym_w[i]}}"
    print(header)
    print("  " + "-" * (col_w + sum(sym_w) + 2 * len(af["alphabet"]) + 4))

    for e in af["etats"]:
        if e in af["initiaux"] and e in af["terminaux"]:
            prefixe = "E/S"
        elif e in af["initiaux"]:
            prefixe = "E"
        elif e in af["terminaux"]:
            prefixe = "S"
        else:
            prefixe = ""

        ligne = f"  {prefixe:3} {str(e):>{col_w}}"
        for i, s in enumerate(af["alphabet"]):
            contenu = table[e][s]
            cellule = ','.join(str(x) for x in sorted(contenu)) if contenu else "--"
            ligne += f"  {cellule:^{sym_w[i]}}"
        print(ligne)

    print(sep)
    print()

#  TESTS : DÉTERMINISTE, STANDARD, COMPLET

def est_deterministe(af):
    raisons = []
    if len(af["initiaux"]) > 1:
        raisons.append(f"  → Plusieurs états initiaux : {af['initiaux']}")

    table = {}
    for (dep, sym, arr) in af["transitions"]:
        # DÉTECTION DE L'EPSILON-TRANSITION
        if sym == 'e':
            raisons.append(f"  → Transition epsilon détectée depuis l'état {dep} (non déterministe)")

        table.setdefault((dep, sym), []).append(arr)

    for (dep, sym), arrivees in table.items():
        if len(arrivees) > 1:
            raisons.append(f"  → État {dep} sur '{sym}' : {arrivees} (non déterministe)")

    return (len(raisons) == 0, raisons)


def est_standard(af):
    raisons = []
    if len(af["initiaux"]) != 1:
        raisons.append(f"  → Nombre d'états initiaux != 1 : {af['initiaux']}")
        return (False, raisons)

    init = af["initiaux"][0]
    for (dep, sym, arr) in af["transitions"]:
        if arr == init:
            raisons.append(f"  → Transition {dep} --{sym}--> {init} (arrive sur l'état initial)")

    return (len(raisons) == 0, raisons)


def est_complet(af):
    raisons = []
    table = {e: {s: [] for s in af["alphabet"]} for e in af["etats"]}
    for (dep, sym, arr) in af["transitions"]:
        if sym in table.get(dep, {}):
            table[dep][sym].append(arr)

    for e in af["etats"]:
        for s in af["alphabet"]:
            if not table[e][s]:
                raisons.append(f"  → État {e} : aucune transition sur '{s}'")

    return (len(raisons) == 0, raisons)


def afficher_proprietes(af):
    print("   Propriétés ")

    det, raisons_det = est_deterministe(af)
    print(f"  Déterministe : {'OUI' if det else 'NON'}")
    if not det:
        for r in raisons_det:
            print(r)

    std, raisons_std = est_standard(af)
    print(f"  Standard     : {'OUI' if std else 'NON'}")
    if not std:
        for r in raisons_std:
            print(r)

    comp, raisons_comp = est_complet(af)
    print(f"  Complet      : {'OUI' if comp else 'NON'}")
    if not comp:
        for r in raisons_comp:
            print(r)

    print()
    return det, std, comp

#  STANDARDISATION

def standardiser(af):
    sfa = copier_automate(af)
    nouvel_init = max(sfa["etats"]) + 1

    nouvelles = []
    for init in sfa["initiaux"]:
        for (dep, sym, arr) in sfa["transitions"]:
            if dep == init:
                nouvelles.append((nouvel_init, sym, arr))

    sfa["transitions"]    += nouvelles
    sfa["nb_transitions"] += len(nouvelles)

    for init in sfa["initiaux"]:
        if init in sfa["terminaux"] and nouvel_init not in sfa["terminaux"]:
            sfa["terminaux"].append(nouvel_init)

    sfa["etats"].append(nouvel_init)
    sfa["nb_etats"] += 1
    sfa["initiaux"]  = [nouvel_init]
    sfa["nom"]       = af["nom"] + "_std"

    return sfa


def nommer_etat(ensemble):
    tri = sorted(ensemble)
    if all(e < 10 for e in tri):
        return ''.join(str(e) for e in tri)
    return '.'.join(str(e) for e in tri)


def completion(af):
    afdc    = copier_automate(af)
    puits   = max(afdc["etats"]) + 1
    puits_utilise = False

    table = {e: {s: None for s in afdc["alphabet"]} for e in afdc["etats"]}
    for (dep, sym, arr) in afdc["transitions"]:
        table[dep][sym] = arr

    nouvelles = []
    for e in list(afdc["etats"]):
        for s in afdc["alphabet"]:
            if table[e][s] is None:
                nouvelles.append((e, s, puits))
                puits_utilise = True

    if puits_utilise:
        afdc["etats"].append(puits)
        afdc["nb_etats"] += 1
        for s in afdc["alphabet"]:
            nouvelles.append((puits, s, puits))
        afdc["transitions"]    += nouvelles
        afdc["nb_transitions"] += len(nouvelles)
        print(f"  → État puits créé : {puits}")

    afdc["nom"] = af["nom"] + "_complet"
    return afdc


def epsilon_fermeture(etats, transitions):
    fermeture = set(etats)
    pile = list(etats)
    while pile:
        e = pile.pop()
        for (dep, sym, arr) in transitions:
            if dep == e and sym == 'e' and arr not in fermeture:
                fermeture.add(arr)
                pile.append(arr)
    return fermeture


def determiniser_et_completer(af):
    print("   Déterminisation (algorithme des sous-ensembles) ")

    etat_init = frozenset(epsilon_fermeture(af["initiaux"], af["transitions"]))
    a_traiter = [etat_init]
    vus       = {etat_init}
    delta     = {}

    while a_traiter:
        courant    = a_traiter.pop(0)
        delta[courant] = {}
        for s in af["alphabet"]:
            arrivees = set()
            for e in courant:
                for (dep, sym, arr) in af["transitions"]:
                    if dep == e and sym == s:
                        arrivees.add(arr)
            if arrivees:
                arrivees = epsilon_fermeture(arrivees, af["transitions"])
            arr_frozen = frozenset(arrivees) if arrivees else frozenset({'P'})
            delta[courant][s] = arr_frozen
            if arr_frozen not in vus:
                vus.add(arr_frozen)
                a_traiter.append(arr_frozen)

    correspondance = {}
    for fs in vus:
        if fs == frozenset({'P'}):
            correspondance['P'] = fs
        else:
            correspondance[nommer_etat(fs)] = fs

    print()
    print("  Correspondance états :")
    for nom, fs in sorted(correspondance.items(), key=lambda x: (len(x[0]), x[0])):
        orig = sorted(str(e) for e in fs) if fs != frozenset({'P'}) else ['∅ (puits)']
        print(f"    {nom:10} ← {{{', '.join(orig)}}}")
    print()

    fs_to_nom  = {v: k for k, v in correspondance.items()}
    noms_etats = list(correspondance.keys())
    nom_to_int = {n: i for i, n in enumerate(noms_etats)}

    afdc = creer_automate()
    afdc["nom"]         = af["nom"] + "_det"
    afdc["alphabet"]    = af["alphabet"][:]
    afdc["nb_symboles"] = af["nb_symboles"]
    afdc["nb_etats"]    = len(noms_etats)
    afdc["etats"]       = list(range(afdc["nb_etats"]))
    afdc["initiaux"]    = [nom_to_int[fs_to_nom[etat_init]]]

    afdc["terminaux"] = []
    for nom, fs in correspondance.items():
        if fs != frozenset({'P'}) and any(e in af["terminaux"] for e in fs):
            afdc["terminaux"].append(nom_to_int[nom])

    afdc["transitions"] = []
    for fs, trans in delta.items():
        dep_int = nom_to_int[fs_to_nom[fs]]
        for s, arr_fs in trans.items():
            arr_int = nom_to_int[fs_to_nom[arr_fs]]
            afdc["transitions"].append((dep_int, s, arr_int))
    afdc["nb_transitions"] = len(afdc["transitions"])

    corresp_finale = {nom_to_int[n]: n for n in noms_etats}
    return afdc, corresp_finale


#  MINIMISATION

def trouver_classe(e, partition):
    for i, classe in enumerate(partition):
        if e in classe:
            return i
    return -1


def minimiser(afdc):
    print("   Minimisation (algorithme des partitions)   ")

    etats_terminaux     = [e for e in afdc["etats"] if e in afdc["terminaux"]]
    etats_non_terminaux = [e for e in afdc["etats"] if e not in afdc["terminaux"]]

    if not etats_terminaux:
        print("  Aucun état terminal : langage vide, minimisation triviale.")
        return copier_automate(afdc), {e: [e] for e in afdc["etats"]}

    partition = [etats_terminaux[:], etats_non_terminaux[:]] if etats_non_terminaux else [etats_terminaux[:]]

    table = {e: {s: None for s in afdc["alphabet"]} for e in afdc["etats"]}
    for (dep, sym, arr) in afdc["transitions"]:
        table[dep][sym] = arr

    num_partition = 0
    while True:
        num_partition += 1
        print(f"\n  Partition P{num_partition} :")
        for i, classe in enumerate(partition):
            print(f"    Classe {i} : {sorted(classe)}")

        print(f"  Transitions (classes) :")
        for i, classe in enumerate(partition):
            e_rep  = classe[0]
            ligne  = f"    Classe {i} :"
            for s in afdc["alphabet"]:
                dest    = table[e_rep][s]
                cl_dest = trouver_classe(dest, partition) if dest is not None else -1
                ligne  += f"  {s}→C{cl_dest}"
            print(ligne)

        nouvelle_partition = []
        for classe in partition:
            sous_classes = {}
            for e in classe:
                signature = tuple(
                    trouver_classe(table[e][s], partition) if table[e][s] is not None else -1
                    for s in afdc["alphabet"]
                )
                sous_classes.setdefault(signature, []).append(e)
            for sc in sous_classes.values():
                nouvelle_partition.append(sc)

        if sorted([sorted(c) for c in nouvelle_partition]) == sorted([sorted(c) for c in partition]):
            print(f"\n  Stabilité atteinte à P{num_partition} → partition finale.")
            break
        partition = nouvelle_partition

    correspondance = {i: sorted(classe) for i, classe in enumerate(partition)}

    afdcm = creer_automate()
    afdcm["nom"]         = afdc["nom"] + "_min"
    afdcm["alphabet"]    = afdc["alphabet"][:]
    afdcm["nb_symboles"] = afdc["nb_symboles"]
    afdcm["nb_etats"]    = len(partition)
    afdcm["etats"]       = list(range(len(partition)))
    afdcm["initiaux"]    = [trouver_classe(afdc["initiaux"][0], partition)]
    afdcm["terminaux"]   = list({trouver_classe(e, partition) for e in afdc["terminaux"]})

    afdcm["transitions"] = []
    for i, classe in enumerate(partition):
        e_rep = classe[0]
        for s in afdc["alphabet"]:
            dest = table[e_rep][s]
            if dest is not None:
                afdcm["transitions"].append((i, s, trouver_classe(dest, partition)))
    afdcm["nb_transitions"] = len(afdcm["transitions"])

    if afdcm["nb_etats"] == afdc["nb_etats"]:
        print("  → L'automate était déjà minimal.")
    else:
        print(f"  → Réduit de {afdc['nb_etats']} à {afdcm['nb_etats']} états.")

    return afdcm, correspondance

#  RECONNAISSANCE DE MOTS

def reconnaitre_mot(mot, afdc):
    for c in mot:
        if c not in afdc["alphabet"]:
            print(f"  Caractère '{c}' hors alphabet {afdc['alphabet']} → NON reconnu")
            return False

    table = {e: {s: None for s in afdc["alphabet"]} for e in afdc["etats"]}
    for (dep, sym, arr) in afdc["transitions"]:
        table[dep][sym] = arr

    etat   = afdc["initiaux"][0]
    chemin = [etat]

    for c in mot:
        suivant = table[etat].get(c)
        if suivant is None:
            print(f"  Chemin : {' → '.join(str(e) for e in chemin)} → BLOQUÉ sur '{c}'")
            print(f"  Résultat : NON reconnu")
            return False
        etat = suivant
        chemin.append(etat)

    reconnu = etat in afdc["terminaux"]
    print(f"  Chemin : {' → '.join(str(e) for e in chemin)}")
    print(f"  État final {etat} {'∈' if reconnu else '∉'} terminaux")
    print(f"  Résultat : {'OUI' if reconnu else 'NON'} reconnu")
    return reconnu

#  LANGAGE COMPLÉMENTAIRE

def complementaire(afdc):
    acomp = copier_automate(afdc)
    acomp["terminaux"] = [e for e in afdc["etats"] if e not in afdc["terminaux"]]
    acomp["nom"]       = afdc["nom"] + "_comp"
    return acomp

#  BOUCLE PRINCIPALE

def choisir_automate():
    print("\n" + "-" * 60)
    print("CHOIX DE L'AUTOMATE")
    print("-" * 60)
    return input("  Entrez le numéro de l'automate (ou 'quitter') : ").strip()


def traiter_automate(numero):
    nom_fichier = f"automates/{numero}.txt"
    if not os.path.exists(nom_fichier):
        nom_fichier = f"automates/{int(numero):02d}.txt"
        if not os.path.exists(nom_fichier):
            print(f"\n  Fichier introuvable pour l'automate n°{numero}.")
            print(f"  Cherché : automates/{numero}.txt et automates/{int(numero):02d}.txt")
            return

    print(f"\n  Chargement de l'automate n°{numero}...")
    af = lire_automate(nom_fichier)
    if af is None:
        return

    afficher_automate(af)
    det, std, comp = afficher_proprietes(af)

    af_courant = af
    if not std:
        rep = input("  Voulez-vous standardiser l'automate ? (oui/non) : ").strip().lower()
        if rep == 'oui':
            af_courant = standardiser(af)
            print("\n  Automate standardisé :")
            afficher_automate(af_courant, "Automate standardisé")
            det, std, comp = afficher_proprietes(af_courant)

    det2, _ = est_deterministe(af_courant)
    comp2, _ = est_complet(af_courant)

    if det2 and comp2:
        print("  L'automate est déjà déterministe et complet → pas de transformation.")
        afdc          = copier_automate(af_courant)
        afdc["nom"]   = af_courant["nom"] + "_AFDC"
        corresp_det   = {e: str(e) for e in afdc["etats"]}
    elif det2 and not comp2:
        print("  L'automate est déterministe mais pas complet → complétion.")
        afdc        = completion(af_courant)
        corresp_det = {e: str(e) for e in afdc["etats"]}
    else:
        print("  L'automate n'est pas déterministe → déterminisation + complétion.")
        afdc, corresp_det = determiniser_et_completer(af_courant)

    print("\n  Automate déterministe et complet (AFDC) :")
    afficher_automate(afdc, "AFDC")

    if corresp_det:
        print("  Correspondance états AFDC → états originaux :")
        for e, orig in sorted(corresp_det.items()):
            print(f"    État {e:3} ← {orig}")
        print()

    print("  Lancement de la minimisation...")
    afdcm, corresp_min = minimiser(afdc)
    print("\n  Automate minimal (AFDCM) :")
    afficher_automate(afdcm, "AFDCM")

    print("  Correspondance états AFDCM → états AFDC :")
    for e, etats_afdc in sorted(corresp_min.items()):
        print(f"    État {e} ← {{{', '.join(str(x) for x in etats_afdc)}}}")
    print()

    print("  Reconnaissance de mots ")
    print(f"  (Automate utilisé : AFDC '{afdc['nom']}')")
    print(f"  Tapez 'fin' pour arrêter la saisie des mots.")
    print(f"  Tapez 'epsilon' ou laissez vide pour tester le mot vide.")

    while True:
        mot = input("\n  Mot à tester : ").strip()
        if mot.lower() == 'fin':
            break
        if mot.lower() == 'epsilon' or mot == '':
            mot = ''
            print(f"  Test du mot vide (ε) :")
        else:
            print(f"  Test du mot '{mot}' :")
        reconnaitre_mot(mot, afdc)

    print("\n  Langage complémentaire ")
    choix_comp = input("  Construire à partir de (1) AFDC ou (2) AFDCM ? : ").strip()
    base  = afdcm if choix_comp == '2' else afdc
    acomp = complementaire(base)
    print(f"\n  Automate complémentaire (base : '{base['nom']}') :")
    afficher_automate(acomp, f"Automate complémentaire de {base['nom']}")


def main():
    print()
    print("  Traitement d'Automates Finis - EFREI P2 2025/2026   ")

    while True:
        rep = choisir_automate()
        if rep.lower() in ('quitter', 'quit', 'q'):
            print("\n  Au revoir !")
            break
        if not rep.lstrip('-').isdigit():
            print("  Entrée invalide. Entrez un numéro ou 'quitter'.")
            continue
        traiter_automate(rep)


if __name__ == "__main__":
    main()