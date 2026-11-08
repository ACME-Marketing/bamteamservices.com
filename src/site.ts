// Facts shown on the site. Sources noted so they can be re-checked.
export const site = {
  name: "BAM Team Services",
  legalName: "BAM Team Services LLC",
  tagline: "Innovation for Good",
  // Florida DOS: filed Nov 5 2018, effective Nov 15 2018, doc L18000258778.
  founded: 2018,
  state: "Florida",
  email: "info@bamteamservices.com",
  mnwUrl: "https://mynursewhitney.com",
};

// Verified on Google Patents, 2026-11-08. Wayne Sheppard is a named inventor on each.
export const patents = [
  {
    family: "Voice-enabled email notification and alerts",
    note: "Hear, forward and reply to email and alerts from any telephone. Assigned to Corybant, Inc.",
    items: [
      { number: "US 7,620,735", id: "US7620735B2", granted: "2009" },
      { number: "US 8,135,791", id: "US8135791B2", granted: "2012" },
    ],
  },
  {
    family: "Multi-tenant contact center callback services",
    note: "Hosted, multi-tenant callback and estimated-wait-time management for contact centers. Assigned to Echopass Corp.",
    items: [
      { number: "US 9,031,223", id: "US9031223B2", granted: "2015" },
      { number: "US 9,602,668", id: "US9602668B2", granted: "2017" },
      { number: "US 9,742,918", id: "US9742918B2", granted: "2017" },
      { number: "US 10,129,404", id: "US10129404B2", granted: "2018" },
    ],
  },
];

// Wayne's career, from his LinkedIn positions. Keep entries factual.
export const timeline = [
  { year: "1992", title: "Founded SpeechCraft, Inc.", body: "Speech recognition for the insurance industry. Built the world's first system for changing an address over the phone in natural, conversational speech, and one of the first internet-based virtual contact centers, for FedEx." },
  { year: "1995", title: "SpeechCraft acquired", body: "Sold to its largest customer." },
  { year: "1996", title: "Genesys Telecommunications Labs", body: "Joined before the IPO. Led large contact center deployments for Bell Atlantic, Bank of America, Citibank and Intel, then directed development of g-Express, demonstrated as a fully integrated contact center deployed live on stage in 60 minutes at G-Force 2001 in Prague." },
  { year: "2001", title: "CTO, Corybant", body: "Architected a voice and web information-delivery platform and shipped its first release in 120 days." },
  { year: "2004", title: "Echopass", body: "Cloud contact centers before the cloud had a name. Won the largest deal in company history, $22 million, and grew the account past 8,000 users." },
  { year: "2018", title: "BAM Team Services founded", body: "A Florida company built on a simple idea: innovation for good." },
  { year: "2020", title: "BAM Air", body: "As schools weighed reopening, we designed HEPA filtration units to help keep classrooms and small businesses safer." },
  { year: "2026", title: "My Nurse Whitney", body: "Private RN care management for families with aging parents." },
];
