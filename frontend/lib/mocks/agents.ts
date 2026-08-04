// Identifiants de démonstration uniquement, aucun compte réel, aucune donnée personnelle.
export interface AgentDemo {
  identifiant: string;
  mot_de_passe: string;
  nom: string;
  agence: string;
}

export const agentsDemo: AgentDemo[] = [
  { identifiant: "agent.be", mot_de_passe: "solida-demo", nom: "Agent Bè", agence: "Agence Bè" },
  {
    identifiant: "agent.agoe",
    mot_de_passe: "solida-demo",
    nom: "Agent Agoè",
    agence: "Agence Agoè",
  },
];

export function verifierIdentifiants(identifiant: string, motDePasse: string): AgentDemo | null {
  const agent = agentsDemo.find((a) => a.identifiant === identifiant);
  if (!agent || agent.mot_de_passe !== motDePasse) return null;
  return agent;
}
