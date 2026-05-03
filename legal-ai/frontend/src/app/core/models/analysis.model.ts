export interface AnalysisState {
  issue: string;
  type: string;
}

export interface Lawyer {
  name: string;
  spec: string;
  rating: number;
  reviews: number;
  chat: number;
  video: number;
  exp: number;
  online: boolean;
  initials: string;
  lang: string;
}

export interface ChatMessage {
  from: 'me' | 'them';
  text: string;
}

export type ConsultMode = 'chat' | 'video';

export type Section = 'pathway' | 'risk' | 'adversarial' | 'settlement';

export interface SectionTab {
  id: Section;
  label: string;
}

export interface LegalStep {
  icon: string;
  title: string;
  detail: string;
}

export interface RiskFactor {
  label: string;
  value: number;
}

export interface AnalysisApiResponse {
  issue: string;
  caseType: string;
  analysis: {
    riskScore: number;
    settlementProbability: number;
    advocatePoints: string[];
    opponentPoints: string[];
    vulnerabilities: string[];
    steps: { title: string; detail: string }[];
    riskFactors: string[] | null;
    riskSummary: string | null;
    advocateConfidence: number;
    opponentConfidence: number;
    riskLabel: string | null;
    detailedFactors: { label: string; value: number; explanation: string }[] | null;
    settlementRecommendation: string | null;
    settlementReasoning: string | null;
    documents: string[] | null;
  };
}
