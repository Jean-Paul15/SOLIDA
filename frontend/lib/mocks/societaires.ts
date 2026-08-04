import type {
  CreditResume,
  DossierSocietaire,
  ResultatRechercheSocietaire,
  SyntheseGroupe,
} from "@/lib/contracts";

function serieSolde(base: number, pas: number, mois: number = 12) {
  return Array.from({ length: mois }, (_, i) => {
    const d = new Date(2026, 7 - (mois - 1 - i), 1);
    return {
      mois: d.toISOString().slice(0, 10),
      solde: Math.max(0, Math.round(base + pas * i)),
    };
  });
}

interface FicheMock {
  recherche: ResultatRechercheSocietaire;
  dossier: DossierSocietaire;
  groupe?: SyntheseGroupe;
}

const creditsAdjo: CreditResume[] = [
  {
    credit_id: "cr-1001",
    date_deblocage: "2023-02-10",
    montant_octroye: 500000,
    duree_mois: 12,
    numero_cycle: 1,
    statut: "solde",
    capital_restant_du: 0,
    max_jours_retard: 0,
  },
  {
    credit_id: "cr-1002",
    date_deblocage: "2024-03-05",
    montant_octroye: 800000,
    duree_mois: 12,
    numero_cycle: 2,
    statut: "en_cours",
    capital_restant_du: 210000,
    max_jours_retard: 0,
  },
];

export const societaires: Record<string, FicheMock> = {
  "soc-adjo": {
    recherche: {
      societaire_id: "soc-adjo",
      nom_complet: "ADJO Kokou Mensah",
      numero_membre: "004512",
      agence: "Agence Bè",
      zone: "semi_urbain",
      statut: "actif",
      a_credit_en_cours: true,
    },
    dossier: {
      identite: {
        societaire_id: "soc-adjo",
        numero_membre: "004512",
        nom_complet: "ADJO Kokou Mensah",
        segment: "salarie",
        agence: "Agence Bè",
        date_adhesion: "2019-03-14",
        anciennete_mois: 64,
        statut: "actif",
        age: 47,
        niveau_instruction: "secondaire",
      },
      activite: {
        secteur: "commerce",
        anciennete_activite_mois: 84,
        revenu_mensuel_declare: 185000,
        charges_mensuelles: 72000,
        capacite_remboursement_estimee: 113000,
        nb_personnes_a_charge: 3,
        parts_sociales_montant: 45000,
      },
      epargne: {
        solde_moyen_6m: 312000,
        tendance_12m: "hausse",
        nb_mois_avec_depot_12m: 11,
        volatilite: 0.14,
        ratio_epargne_revenu: 0.42,
        anciennete_relation_mois: 64,
        serie_solde_12m: serieSolde(240000, 6500),
      },
      historique_credit: creditsAdjo,
      alertes: [],
    },
  },

  "soc-kossi": {
    recherche: {
      societaire_id: "soc-kossi",
      nom_complet: "KOSSI Ama Efua",
      numero_membre: "007821",
      agence: "Agence Bè",
      zone: "urbain",
      statut: "actif",
      a_credit_en_cours: false,
    },
    dossier: {
      identite: {
        societaire_id: "soc-kossi",
        numero_membre: "007821",
        nom_complet: "KOSSI Ama Efua",
        segment: "individuel",
        agence: "Agence Bè",
        date_adhesion: "2025-01-20",
        anciennete_mois: 19,
        statut: "actif",
        age: 26,
        niveau_instruction: "superieur",
      },
      activite: {
        secteur: "artisanat",
        anciennete_activite_mois: 30,
        revenu_mensuel_declare: 95000,
        charges_mensuelles: 40000,
        capacite_remboursement_estimee: 55000,
        nb_personnes_a_charge: 0,
        parts_sociales_montant: 15000,
      },
      epargne: {
        solde_moyen_6m: 68000,
        tendance_12m: "stable",
        nb_mois_avec_depot_12m: 8,
        volatilite: 0.31,
        ratio_epargne_revenu: 0.29,
        anciennete_relation_mois: 19,
        serie_solde_12m: serieSolde(55000, 1200),
      },
      historique_credit: [],
      alertes: [],
    },
  },

  "soc-akossiwa": {
    recherche: {
      societaire_id: "soc-akossiwa",
      nom_complet: "AKOSSIWA Delali Kponvi",
      numero_membre: "011240",
      agence: "Agence Agoè",
      zone: "rural",
      statut: "actif",
      a_credit_en_cours: true,
    },
    dossier: {
      identite: {
        societaire_id: "soc-akossiwa",
        numero_membre: "011240",
        nom_complet: "AKOSSIWA Delali Kponvi",
        segment: "femme_gie",
        agence: "Agence Agoè",
        date_adhesion: "2021-06-02",
        anciennete_mois: 50,
        statut: "actif",
        age: 39,
        niveau_instruction: "primaire",
      },
      activite: {
        secteur: "agriculture",
        anciennete_activite_mois: 60,
        revenu_mensuel_declare: 130000,
        charges_mensuelles: 58000,
        capacite_remboursement_estimee: 72000,
        nb_personnes_a_charge: 4,
        parts_sociales_montant: 30000,
      },
      epargne: {
        solde_moyen_6m: 145000,
        tendance_12m: "hausse",
        nb_mois_avec_depot_12m: 10,
        volatilite: 0.2,
        ratio_epargne_revenu: 0.31,
        anciennete_relation_mois: 50,
        serie_solde_12m: serieSolde(100000, 3800),
      },
      historique_credit: [
        {
          credit_id: "cr-2001",
          date_deblocage: "2022-04-01",
          montant_octroye: 300000,
          duree_mois: 9,
          numero_cycle: 1,
          statut: "solde",
          capital_restant_du: 0,
          max_jours_retard: 0,
        },
        {
          credit_id: "cr-2002",
          date_deblocage: "2023-06-01",
          montant_octroye: 450000,
          duree_mois: 12,
          numero_cycle: 2,
          statut: "solde",
          capital_restant_du: 0,
          max_jours_retard: 5,
        },
        {
          credit_id: "cr-2003",
          date_deblocage: "2024-08-01",
          montant_octroye: 600000,
          duree_mois: 12,
          numero_cycle: 3,
          statut: "en_cours",
          capital_restant_du: 180000,
          max_jours_retard: 0,
        },
      ],
      alertes: [],
    },
    groupe: {
      groupe_id: "grp-espoir",
      nom_groupe: "Groupement Espoir d'Agoè",
      taille_actuelle: 9,
      date_creation: "2021-05-15",
      taux_remboursement_groupe: 0.97,
      nb_cycles_completes: 3,
      nb_sorties_12m: 0,
      statut: "actif",
      membres: [
        {
          societaire_id: "soc-akossiwa",
          nom_complet: "AKOSSIWA Delali Kponvi",
          role: "presidente",
          anciennete_mois: 50,
          statut_credit: "en_cours",
          caution_appelee: false,
        },
        {
          societaire_id: "soc-membre-2",
          nom_complet: "ABLA Sena Dogbe",
          role: "tresoriere",
          anciennete_mois: 48,
          statut_credit: "en_cours",
          caution_appelee: false,
        },
        {
          societaire_id: "soc-membre-3",
          nom_complet: "AFI Yawa Kutor",
          role: "membre",
          anciennete_mois: 41,
          statut_credit: "solde",
          caution_appelee: false,
        },
      ],
    },
  },

  "soc-mawuli": {
    recherche: {
      societaire_id: "soc-mawuli",
      nom_complet: "MAWULI Ayélé Foli",
      numero_membre: "013905",
      agence: "Agence Agoè",
      zone: "rural",
      statut: "actif",
      a_credit_en_cours: true,
    },
    dossier: {
      identite: {
        societaire_id: "soc-mawuli",
        numero_membre: "013905",
        nom_complet: "MAWULI Ayélé Foli",
        segment: "femme_gie",
        agence: "Agence Agoè",
        date_adhesion: "2022-02-11",
        anciennete_mois: 42,
        statut: "actif",
        age: 33,
        niveau_instruction: "aucun",
      },
      activite: {
        secteur: "agriculture",
        anciennete_activite_mois: 48,
        revenu_mensuel_declare: 78000,
        charges_mensuelles: 41000,
        capacite_remboursement_estimee: 37000,
        nb_personnes_a_charge: 5,
        parts_sociales_montant: 10000,
      },
      epargne: {
        solde_moyen_6m: 41000,
        tendance_12m: "erosion",
        nb_mois_avec_depot_12m: 6,
        volatilite: 0.48,
        ratio_epargne_revenu: 0.11,
        anciennete_relation_mois: 42,
        serie_solde_12m: serieSolde(70000, -2600),
      },
      historique_credit: [
        {
          credit_id: "cr-3001",
          date_deblocage: "2023-03-01",
          montant_octroye: 250000,
          duree_mois: 9,
          numero_cycle: 1,
          statut: "en_souffrance",
          capital_restant_du: 95000,
          max_jours_retard: 47,
        },
      ],
      alertes: ["Retard de remboursement en cours sur le crédit cr-3001."],
    },
    groupe: {
      groupe_id: "grp-renaissance",
      nom_groupe: "Groupement Renaissance",
      taille_actuelle: 6,
      date_creation: "2022-01-20",
      taux_remboursement_groupe: 0.61,
      nb_cycles_completes: 1,
      nb_sorties_12m: 2,
      statut: "en_difficulte",
      membres: [
        {
          societaire_id: "soc-mawuli",
          nom_complet: "MAWULI Ayélé Foli",
          role: "membre",
          anciennete_mois: 42,
          statut_credit: "en_souffrance",
          caution_appelee: true,
        },
      ],
    },
  },

  "soc-koffi": {
    recherche: {
      societaire_id: "soc-koffi",
      nom_complet: "KOFFI Yao Adjovi",
      numero_membre: "015230",
      agence: "Agence Bè",
      zone: "urbain",
      statut: "actif",
      a_credit_en_cours: false,
    },
    dossier: {
      identite: {
        societaire_id: "soc-koffi",
        numero_membre: "015230",
        nom_complet: "KOFFI Yao Adjovi",
        segment: "individuel",
        agence: "Agence Bè",
        date_adhesion: "2024-05-06",
        anciennete_mois: 15,
        statut: "actif",
        age: 24,
        niveau_instruction: "secondaire",
      },
      activite: {
        secteur: "commerce",
        anciennete_activite_mois: 20,
        capacite_remboursement_estimee: 48000,
        nb_personnes_a_charge: 1,
        parts_sociales_montant: 10000,
      },
      epargne: {
        solde_moyen_6m: 89000,
        tendance_12m: "stable",
        nb_mois_avec_depot_12m: 9,
        volatilite: 0.22,
        ratio_epargne_revenu: 0.33,
        anciennete_relation_mois: 15,
        serie_solde_12m: serieSolde(75000, 1300),
      },
      historique_credit: [],
      alertes: [],
    },
  },
};

const combiningMarks = new RegExp("[̀-ͯ]", "g");

function normalise(s: string) {
  return s.normalize("NFD").replace(combiningMarks, "").toLowerCase();
}

export function rechercherSocietaires(terme: string): ResultatRechercheSocietaire[] {
  const motsCibles = normalise(terme).split(/\s+/).filter(Boolean);
  return Object.values(societaires)
    .map((f) => f.recherche)
    .filter((r) => {
      const nom = normalise(r.nom_complet);
      const correspondNom = motsCibles.every((mot) => nom.includes(mot));
      return correspondNom || r.numero_membre.includes(terme);
    });
}
