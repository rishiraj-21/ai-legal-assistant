import { Lawyer } from '../models/analysis.model';

export const LAWYERS: Lawyer[] = [
  { name: 'Aditi Sharma', spec: 'Family & Divorce', rating: 4.9, reviews: 1284, chat: 25, video: 60, exp: 12, online: true, initials: 'AS', lang: 'EN · HI' },
  { name: 'Rohan Mehta', spec: 'Corporate & M&A', rating: 4.8, reviews: 932, chat: 40, video: 90, exp: 15, online: true, initials: 'RM', lang: 'EN' },
  { name: 'Nisha Verma', spec: 'Criminal Defense', rating: 4.9, reviews: 2105, chat: 30, video: 75, exp: 18, online: false, initials: 'NV', lang: 'EN · HI · MR' },
  { name: 'Arjun Kapoor', spec: 'Property & Real Estate', rating: 4.7, reviews: 748, chat: 20, video: 55, exp: 9, online: true, initials: 'AK', lang: 'EN · HI' },
  { name: 'Priya Nair', spec: 'Consumer & Civil', rating: 4.8, reviews: 611, chat: 18, video: 48, exp: 7, online: true, initials: 'PN', lang: 'EN · ML' },
  { name: 'Karan Iyer', spec: 'Intellectual Property', rating: 4.9, reviews: 489, chat: 35, video: 80, exp: 11, online: false, initials: 'KI', lang: 'EN · TA' },
];

export const CASE_TYPES = [
  'Criminal', 'Civil', 'Family', 'Property', 'Corporate',
  'Employment', 'Consumer', 'Intellectual Property', 'Tax', 'Other',
];

export const ANALYSIS_STEPS = [
  'Reviewing legal context...',
  'Analyzing case precedents...',
  'Computing risk assessment...',
  'Running adversarial simulation...',
  'Generating settlement strategy...',
];

export const CONSULT_FILTERS = ['All', 'Family', 'Criminal', 'Property', 'Corporate', 'Consumer', 'IP'];
