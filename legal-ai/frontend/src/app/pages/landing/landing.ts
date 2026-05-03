import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { LucideAngularModule, ArrowRight, Sparkles, Scale, Shield, Gavel, Brain, Users, CheckCircle2, Quote, Star, FileText, MessageCircle } from 'lucide-angular';
import { Navbar } from '../../shared/components/navbar/navbar';

@Component({
  selector: 'app-landing',
  imports: [RouterLink, LucideAngularModule, Navbar],
  templateUrl: './landing.html',
  styleUrl: './landing.css'
})
export default class Landing {
  readonly ArrowRightIcon = ArrowRight;
  readonly SparklesIcon = Sparkles;
  readonly ScaleIcon = Scale;
  readonly ShieldIcon = Shield;
  readonly GavelIcon = Gavel;
  readonly BrainIcon = Brain;
  readonly UsersIcon = Users;
  readonly CheckCircle2Icon = CheckCircle2;
  readonly QuoteIcon = Quote;
  readonly StarIcon = Star;
  readonly FileTextIcon = FileText;
  readonly MessageCircleIcon = MessageCircle;

  readonly features = [
    { icon: this.BrainIcon, title: 'Legal Pathway', desc: 'AI maps every procedural step from filing to resolution.' },
    { icon: this.ShieldIcon, title: 'Risk Scoring', desc: 'Quantify your exposure with a precedent-aware risk index.' },
    { icon: this.GavelIcon, title: 'Adversarial Simulation', desc: 'Advocate vs. Opponent AI \u2014 see both sides before they do.' },
    { icon: this.UsersIcon, title: 'Human Lawyers', desc: 'Escalate to a verified advocate over chat or video anytime.' },
  ];

  readonly steps = [
    { n: '01', title: 'Create your account', desc: 'Sign up in under a minute \u2014 your case stays private.' },
    { n: '02', title: 'Describe your case', desc: 'Plain language. No legalese. Lex understands context.' },
    { n: '03', title: 'Get instant clarity', desc: 'Pathway, risk, and negotiation playbook \u2014 all in one report.' },
  ];

  readonly stats = [
    { v: '12k+', l: 'Cases analyzed' },
    { v: '4.9', l: 'Avg. user rating' },
    { v: '180+', l: 'Verified lawyers' },
    { v: '30s', l: 'Avg. report time' },
  ];

  readonly testimonials = [
    {
      quote: 'Lex saved me weeks of confusion. The risk score and pathway gave me real clarity before my first lawyer meeting.',
      name: 'Meera K.',
      role: 'Founder \u00b7 Mumbai',
    },
    {
      quote: "The adversarial simulation showed me arguments I hadn't considered. Felt like having a senior advocate in my pocket.",
      name: 'Vikram S.',
      role: 'Real estate investor',
    },
    {
      quote: 'Booked a chat with a property lawyer in two minutes. Smooth, premium, and genuinely helpful.',
      name: 'Anjali R.',
      role: 'HR Lead',
    },
  ];

  readonly trustBadges = [
    'End-to-end confidential',
    'Trained on verified precedent',
    'Human lawyers on standby',
  ];

  readonly heroBadges = ['Confidential', 'Not legal advice', 'Precedent-aware', 'Built with care'];

  readonly currentYear = new Date().getFullYear();

  starsArray = [...Array(5)].map((_, i) => i);
}
