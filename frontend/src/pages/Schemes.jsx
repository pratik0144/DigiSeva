import React from 'react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { useSession } from '../context/SessionContext';
import { CheckCircle2, FileText, IndianRupee } from 'lucide-react';

export const Schemes = () => {
  const { schemes } = useSession();

  // Mock extended data for the demo
  const schemeDetails = {
    "PM-KISAN": {
      title: "PM-KISAN Samman Nidhi",
      desc: "₹6000/year income support for landholding farmers.",
      status: "Active",
      amount: "₹2,000 Next Installment",
      date: "Nov 2023"
    },
    "MGNREGA": {
      title: "MGNREGA",
      desc: "100 days of guaranteed wage employment.",
      status: "Available to apply",
      amount: "₹220/day",
      date: "-"
    }
  };

  const activeSchemes = schemes || ["PM-KISAN"];

  return (
    <div className="max-w-4xl mx-auto w-full">
      <div className="mb-6">
        <h2 className="h2 text-primary">Government Schemes</h2>
        <p className="body-sm text-secondary mt-1">Discover and track your financial benefits</p>
      </div>

      <h3 className="label text-secondary uppercase mb-4">Your Active Schemes</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        {activeSchemes.map((schemeName) => {
          const detail = schemeDetails[schemeName] || { title: schemeName, desc: "Government Scheme", status: "Active" };
          return (
            <Card key={schemeName} className="border-l-4 border-l-primary flex flex-col">
              <div className="flex justify-between items-start mb-2">
                <h4 className="font-bold text-lg">{detail.title}</h4>
                <div className="flex items-center gap-1 text-xs font-bold text-primary bg-primary-container px-2 py-1 rounded-full">
                  <CheckCircle2 size={12} />
                  <span>{detail.status}</span>
                </div>
              </div>
              <p className="body-sm text-secondary mb-4 flex-1">{detail.desc}</p>
              
              <div className="bg-surface-container p-3 rounded-md flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <IndianRupee size={16} className="text-primary" />
                  <span className="font-semibold">{detail.amount}</span>
                </div>
                <span className="text-xs text-secondary">Due: {detail.date}</span>
              </div>
            </Card>
          );
        })}
      </div>

      <h3 className="label text-secondary uppercase mb-4">Recommended For You</h3>
      <div className="grid grid-cols-1 gap-4">
        <Card className="flex flex-col md:flex-row gap-4 items-start md:items-center">
          <div className="w-12 h-12 rounded-full bg-surface-container flex items-center justify-center shrink-0">
            <FileText size={24} className="text-primary" />
          </div>
          <div className="flex-1">
            <h4 className="font-bold mb-1">PM Jeevan Jyoti Bima Yojana</h4>
            <p className="body-sm text-secondary">Life insurance cover of ₹2 lakh at just ₹436 per year. Auto-debit available.</p>
          </div>
          <Button variant="secondary" className="w-full md:w-auto shrink-0">
            Check Eligibility
          </Button>
        </Card>

        <Card className="flex flex-col md:flex-row gap-4 items-start md:items-center">
          <div className="w-12 h-12 rounded-full bg-surface-container flex items-center justify-center shrink-0">
            <FileText size={24} className="text-primary" />
          </div>
          <div className="flex-1">
            <h4 className="font-bold mb-1">PM Mudra Yojana</h4>
            <p className="body-sm text-secondary">Micro-loans up to ₹10 lakh for small businesses and non-corporate enterprises.</p>
          </div>
          <Button variant="secondary" className="w-full md:w-auto shrink-0">
            Apply Now
          </Button>
        </Card>
      </div>
    </div>
  );
};
