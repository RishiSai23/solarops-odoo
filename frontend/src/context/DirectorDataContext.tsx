import React, { createContext, useContext, useState } from 'react';
import { directorProjects as seedProjects } from '../data/directorDashboardData';
import { surveys as seedSurveys, installations as seedInstallations, packages as seedPackages } from '../data/directorModulesData';
import type { DirectorProject } from '../data/directorDashboardData';
import type { Survey, Installation, Package } from '../data/directorModulesData';

interface DirectorData {
  projects: DirectorProject[];
  setProjects: React.Dispatch<React.SetStateAction<DirectorProject[]>>;
  surveys: Survey[];
  setSurveys: React.Dispatch<React.SetStateAction<Survey[]>>;
  installations: Installation[];
  setInstallations: React.Dispatch<React.SetStateAction<Installation[]>>;
  packages: Package[];
  setPackages: React.Dispatch<React.SetStateAction<Package[]>>;
}

const Ctx = createContext<DirectorData | null>(null);

export function DirectorDataProvider({ children }: { children: React.ReactNode }) {
  const [projects, setProjects] = useState<DirectorProject[]>(seedProjects);
  const [surveys, setSurveys] = useState<Survey[]>(seedSurveys);
  const [installations, setInstallations] = useState<Installation[]>(seedInstallations);
  const [packages, setPackages] = useState<Package[]>(seedPackages);
  return (
    <Ctx.Provider value={{ projects, setProjects, surveys, setSurveys, installations, setInstallations, packages, setPackages }}>
      {children}
    </Ctx.Provider>
  );
}

export function useDirectorData() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error('DirectorDataProvider missing');
  return ctx;
}
