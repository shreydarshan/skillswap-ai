// DEMO DATA
// Used only for UI development/testing.
// Not used as authenticated user data.

export const CURRENT_USER = {
  id: 'user-0',
  name: 'Alex Rivera',
  username: 'alex_rivera',
  avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&auto=format&fit=crop&q=80',
  role: 'Computer Science Student',
  major: 'Computer Science & Engineering',
  university: 'Stanford University',
  year: 'Junior (3rd Year)',
  location: 'Palo Alto, CA (On-Campus)',
  bio: 'Passionate full-stack developer interested in React, AI applications, and UI design. Looking to improve my Figma skill set in exchange for teaching Frontend Web Development or Python basics!',
  rating: 4.95,
  reviewCount: 24,
  completedSwaps: 14,
  ongoingSwaps: 2,
  availability: 'Mon & Wed 4-7 PM, Weekends 10 AM-2 PM',
  badge: 'Top Educator',
  skillsOffered: [
    { id: 's1', name: 'React.js', level: 'Expert', endorsementCount: 19 },
    { id: 's2', name: 'Python', level: 'Advanced', endorsementCount: 14 },
    { id: 's3', name: 'Tailwind CSS', level: 'Expert', endorsementCount: 12 },
    { id: 's4', name: 'JavaScript (ES6+)', level: 'Advanced', endorsementCount: 16 }
  ],
  skillsWanted: [
    { id: 'w1', name: 'Figma UI/UX Design', urgency: 'High' },
    { id: 'w2', name: 'Spanish Conversation', urgency: 'Medium' },
    { id: 'w3', name: 'Machine Learning', urgency: 'High' }
  ],
  reviews: [
    {
      id: 'r1',
      reviewerName: 'Sophia Chen',
      reviewerAvatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&auto=format&fit=crop&q=80',
      rating: 5,
      date: '2 days ago',
      swapTopic: 'React.js for Figma Basics',
      comment: 'Alex is an awesome mentor! He broke down React hooks clearly in just 2 sessions. Highly recommended!'
    },
    {
      id: 'r2',
      reviewerName: 'Marcus Vance',
      reviewerAvatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80',
      rating: 5,
      date: '1 week ago',
      swapTopic: 'Python for Linear Algebra',
      comment: 'Super structured sessions and great notes provided. We swapped Python scripts for math problem sets.'
    }
  ]
};

export const MOCK_STUDENTS = [
  {
    id: 'user-1',
    name: 'Sophia Chen',
    username: 'sophiadesign',
    avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&auto=format&fit=crop&q=80',
    role: 'UI/UX Design Major',
    major: 'Interaction Design & HCI',
    university: 'Stanford University',
    year: 'Senior (4th Year)',
    location: 'Stanford Campus / Remote',
    bio: 'Figma addict & Design System fanatic. I love building intuitive component libraries. Looking for a patient peer to help me master React fundamentals for my portfolio site!',
    rating: 4.9,
    reviewCount: 31,
    completedSwaps: 18,
    ongoingSwaps: 3,
    availability: 'Tues/Thurs 2-6 PM',
    responseTime: '< 15 mins',
    badge: 'Design Expert',
    matchPercentage: 98,
    matchReasons: [
      'Teaches Figma UI/UX Design which matches your #1 goal',
      'Wants to learn React.js which is your top offered skill',
      'Both students at Stanford University',
      'Matching availability on weekday afternoons'
    ],
    skillsOffered: [
      { id: 'so1', name: 'Figma UI/UX Design', level: 'Expert', endorsementCount: 28 },
      { id: 'so2', name: 'Wireframing & Prototyping', level: 'Expert', endorsementCount: 22 },
      { id: 'so3', name: 'Design Systems', level: 'Advanced', endorsementCount: 15 }
    ],
    skillsWanted: [
      { id: 'sw1', name: 'React.js', urgency: 'High' },
      { id: 'sw2', name: 'Tailwind CSS', urgency: 'Medium' }
    ],
    reviews: [
      {
        id: 'rev1',
        reviewerName: 'Alex Rivera',
        reviewerAvatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80',
        rating: 5,
        date: '3 weeks ago',
        swapTopic: 'Figma Auto-Layout Tutorial',
        comment: 'Sophia is super clear and structured. My design files are 10x cleaner now!'
      }
    ]
  },
  {
    id: 'user-2',
    name: 'Marcus Vance',
    username: 'marcus_ai',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&auto=format&fit=crop&q=80',
    role: 'AI & Data Science Scholar',
    major: 'Applied Mathematics & CS',
    university: 'Stanford University',
    year: 'Master Student',
    location: 'Gates CS Building',
    bio: 'Specializing in Machine Learning models & PyTorch. I can help you understand neural nets or linear algebra in exchange for Web Frontend or JavaScript help.',
    rating: 4.88,
    reviewCount: 19,
    completedSwaps: 11,
    ongoingSwaps: 1,
    availability: 'Evenings after 6 PM',
    responseTime: '< 1 hour',
    badge: 'AI Specialist',
    matchPercentage: 94,
    matchReasons: [
      'Offers Machine Learning (matches your wanted skill)',
      'Wants JavaScript & Web Frontend skills you possess',
      'High rating and quick response rate'
    ],
    skillsOffered: [
      { id: 'so4', name: 'Machine Learning', level: 'Expert', endorsementCount: 20 },
      { id: 'so5', name: 'Python & PyTorch', level: 'Expert', endorsementCount: 24 },
      { id: 'so6', name: 'Data Visualization', level: 'Advanced', endorsementCount: 11 }
    ],
    skillsWanted: [
      { id: 'sw3', name: 'React.js', urgency: 'High' },
      { id: 'sw4', name: 'JavaScript (ES6+)', urgency: 'Medium' }
    ],
    reviews: []
  },
  {
    id: 'user-3',
    name: 'Elena Rostova',
    username: 'elena_polyglot',
    avatar: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&auto=format&fit=crop&q=80',
    role: 'Linguistics & International Relations',
    major: 'Linguistics & Spanish Lit',
    university: 'UC Berkeley',
    year: 'Junior (3rd Year)',
    location: 'Berkeley / Online',
    bio: 'Native Spanish speaker & Polyglot. Love cultural exchange and conversational practice! Looking for someone to guide me through basic coding and website setup.',
    rating: 4.97,
    reviewCount: 42,
    completedSwaps: 26,
    ongoingSwaps: 4,
    availability: 'Flexible / Online Zoom',
    responseTime: '< 30 mins',
    badge: 'Language Master',
    matchPercentage: 91,
    matchReasons: [
      'Teaches Spanish Conversation (matches your wanted skill)',
      'Wants Python / Basic Web Dev assistance',
      'Highest overall rating in Language category'
    ],
    skillsOffered: [
      { id: 'so7', name: 'Spanish Conversation', level: 'Native', endorsementCount: 38 },
      { id: 'so8', name: 'Russian Language', level: 'Native', endorsementCount: 19 },
      { id: 'so9', name: 'Essay Proofreading', level: 'Expert', endorsementCount: 14 }
    ],
    skillsWanted: [
      { id: 'sw5', name: 'Python', urgency: 'High' },
      { id: 'sw6', name: 'HTML & CSS', urgency: 'Medium' }
    ],
    reviews: []
  },
  {
    id: 'user-4',
    name: 'David Kim',
    username: 'dkim_video',
    avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&auto=format&fit=crop&q=80',
    role: 'Film & Media Arts Major',
    major: 'Cinema & Media Production',
    university: 'Stanford University',
    year: 'Sophomore (2nd Year)',
    location: 'Tressider Union / Remote',
    bio: 'Content creator with 50k YouTube subscribers. I teach DaVinci Resolve & Premiere Pro video editing. Seeking math tutoring for Physics II!',
    rating: 4.82,
    reviewCount: 15,
    completedSwaps: 9,
    ongoingSwaps: 2,
    availability: 'Friday & Weekends',
    responseTime: '< 2 hours',
    badge: 'Media Creator',
    matchPercentage: 85,
    matchReasons: [
      'Top rated video creator on campus',
      'Active student on campus',
      'Offers high-demand multimedia skills'
    ],
    skillsOffered: [
      { id: 'so10', name: 'Video Editing (Premiere)', level: 'Expert', endorsementCount: 16 },
      { id: 'so11', name: 'YouTube Content Strategy', level: 'Advanced', endorsementCount: 12 },
      { id: 'so12', name: 'Color Grading', level: 'Intermediate', endorsementCount: 8 }
    ],
    skillsWanted: [
      { id: 'sw7', name: 'Physics II Tutoring', urgency: 'High' },
      { id: 'sw8', name: 'Calculus III', urgency: 'High' }
    ],
    reviews: []
  },
  {
    id: 'user-5',
    name: 'Aaliyah Patel',
    username: 'aaliyah_growth',
    avatar: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&auto=format&fit=crop&q=80',
    role: 'Business Analytics & Marketing',
    major: 'Business Administration',
    university: 'Stanford Graduate School of Business',
    year: 'MBA 1st Year',
    location: 'Knight Management Center',
    bio: 'Ex-tech marketer now pursuing MBA. Can teach digital marketing, pitch pitch deck design, and SEO strategies. Looking for a Python coding tutor!',
    rating: 4.92,
    reviewCount: 22,
    completedSwaps: 15,
    ongoingSwaps: 2,
    availability: 'Monday & Friday Mornings',
    responseTime: '< 45 mins',
    badge: 'Business Mentor',
    matchPercentage: 88,
    matchReasons: [
      'Wants Python skills (matches your top offered skill)',
      'Offers high-value pitch deck & growth marketing skills',
      'Extremely high student review rating'
    ],
    skillsOffered: [
      { id: 'so13', name: 'Digital Marketing', level: 'Expert', endorsementCount: 21 },
      { id: 'so14', name: 'Pitch Deck Coaching', level: 'Expert', endorsementCount: 18 },
      { id: 'so15', name: 'SEO & Analytics', level: 'Advanced', endorsementCount: 14 }
    ],
    skillsWanted: [
      { id: 'sw9', name: 'Python', urgency: 'High' },
      { id: 'sw10', name: 'SQL & Database Basics', urgency: 'Medium' }
    ],
    reviews: []
  }
];
