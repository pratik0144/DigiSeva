import React, { useState } from 'react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { BookOpen, ShieldCheck, TrendingUp, PlayCircle } from 'lucide-react';

export const Education = () => {
  const [activeTab, setActiveTab] = useState('all');

  const topics = [
    {
      id: 1,
      title: "Safe UPI Payments",
      category: "security",
      icon: <ShieldCheck className="text-primary" size={24} />,
      readTime: "3 min read",
      desc: "Learn how to spot fake QR codes and never enter your PIN to receive money.",
    },
    {
      id: 2,
      title: "Understanding Crop Insurance",
      category: "schemes",
      icon: <BookOpen className="text-primary" size={24} />,
      readTime: "5 min read",
      desc: "A simple guide to PMFBY and how to claim it during adverse weather.",
    },
    {
      id: 3,
      title: "Saving for the Future",
      category: "savings",
      icon: <TrendingUp className="text-primary" size={24} />,
      readTime: "2 min video",
      isVideo: true,
      desc: "The magic of compound interest and recurring deposits.",
    }
  ];

  return (
    <div className="max-w-4xl mx-auto w-full">
      <div className="mb-6">
        <h2 className="h2 text-primary">Financial Literacy</h2>
        <p className="body-sm text-secondary mt-1">Simple lessons to build your financial confidence.</p>
      </div>

      <div className="flex gap-2 overflow-x-auto pb-2 mb-6 hide-scrollbar">
        <button 
          onClick={() => setActiveTab('all')}
          className={`px-4 py-2 rounded-full whitespace-nowrap text-sm font-semibold transition-colors ${activeTab === 'all' ? 'bg-primary text-on-primary' : 'bg-surface-container text-on-surface hover:bg-surface-container-high'}`}
        >
          All Topics
        </button>
        <button 
          onClick={() => setActiveTab('security')}
          className={`px-4 py-2 rounded-full whitespace-nowrap text-sm font-semibold transition-colors ${activeTab === 'security' ? 'bg-primary text-on-primary' : 'bg-surface-container text-on-surface hover:bg-surface-container-high'}`}
        >
          Security & Fraud
        </button>
        <button 
          onClick={() => setActiveTab('schemes')}
          className={`px-4 py-2 rounded-full whitespace-nowrap text-sm font-semibold transition-colors ${activeTab === 'schemes' ? 'bg-primary text-on-primary' : 'bg-surface-container text-on-surface hover:bg-surface-container-high'}`}
        >
          Govt Schemes
        </button>
        <button 
          onClick={() => setActiveTab('savings')}
          className={`px-4 py-2 rounded-full whitespace-nowrap text-sm font-semibold transition-colors ${activeTab === 'savings' ? 'bg-primary text-on-primary' : 'bg-surface-container text-on-surface hover:bg-surface-container-high'}`}
        >
          Savings
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {topics.filter(t => activeTab === 'all' || t.category === activeTab).map((topic) => (
          <Card key={topic.id} className="flex flex-col h-full hover:shadow-md transition-shadow cursor-pointer">
            <div className="flex items-start justify-between mb-4">
              <div className="w-12 h-12 rounded-full bg-surface-container flex items-center justify-center">
                {topic.icon}
              </div>
              <span className="text-xs font-bold text-secondary bg-surface-variant px-2 py-1 rounded-sm uppercase tracking-wide">
                {topic.category}
              </span>
            </div>
            <h3 className="h3 mb-2">{topic.title}</h3>
            <p className="body-sm text-secondary mb-6 flex-1">{topic.desc}</p>
            <div className="flex items-center justify-between mt-auto pt-4 border-t border-surface-variant">
              <span className="text-sm font-semibold text-secondary flex items-center gap-1">
                {topic.isVideo ? <PlayCircle size={16} /> : <BookOpen size={16} />}
                {topic.readTime}
              </span>
              <Button variant="secondary" className="!min-h-0 !py-1 !px-4 text-sm">
                {topic.isVideo ? 'Watch' : 'Read'}
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};
