'use client';

import { MapPin, Building2 } from 'lucide-react';

interface HospitalCardProps {
  name: string;
  address: string;
  city: string;
}

export default function HospitalCard({
  name,
  address,
  city,
}: HospitalCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow p-5 border border-gray-100">
      <div className="flex items-start gap-3">
        <div className="bg-blue-100 p-2 rounded-lg">
          <Building2 className="w-6 h-6 text-blue-600" />
        </div>
        
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {name}
          </h3>
          
          <div className="space-y-2 text-sm text-gray-600">
            <div className="flex items-start gap-2">
              <MapPin className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <span>
                {address}, {city}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}