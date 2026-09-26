import React, { createContext, useContext, useState, useEffect } from 'react';

type Theme = 'light' | 'dark' | 'system';
type Density = 'comfortable' | 'compact';

interface PreferencesContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  density: Density;
  setDensity: (density: Density) => void;
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (collapsed: boolean) => void;
}

const PreferencesContext = createContext<PreferencesContextType | undefined>(undefined);

export const PreferencesProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setThemeState] = useState<Theme>('light');
  const [density, setDensityState] = useState<Density>('comfortable');
  const [sidebarCollapsed, setSidebarCollapsedState] = useState<boolean>(false);

  // Initialize from localStorage
  useEffect(() => {
    try {
      const storedTheme = localStorage.getItem('krishiguard-theme') as Theme;
      if (['light', 'dark', 'system'].includes(storedTheme)) setThemeState(storedTheme);

      const storedDensity = localStorage.getItem('krishiguard-density') as Density;
      if (['comfortable', 'compact'].includes(storedDensity)) setDensityState(storedDensity);

      const storedSidebar = localStorage.getItem('krishiguard-sidebar');
      if (storedSidebar !== null) setSidebarCollapsedState(storedSidebar === 'true');
    } catch (e) {
      console.error('Failed to load preferences from localStorage', e);
    }
  }, []);

  // Update theme and apply to document body
  useEffect(() => {
    const applyTheme = (currentTheme: Theme) => {
      const root = window.document.documentElement;
      root.classList.remove('light', 'dark');

      if (currentTheme === 'system') {
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        root.classList.add(systemPrefersDark ? 'dark' : 'light');
      } else {
        root.classList.add(currentTheme);
      }
    };

    applyTheme(theme);
    
    // Listen for system changes if set to system
    if (theme === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = () => applyTheme('system');
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
  }, [theme]);

  // Setters with localStorage persistence
  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
    try { localStorage.setItem('krishiguard-theme', newTheme); } catch (e) {}
  };

  const setDensity = (newDensity: Density) => {
    setDensityState(newDensity);
    try { localStorage.setItem('krishiguard-density', newDensity); } catch (e) {}
  };

  const setSidebarCollapsed = (collapsed: boolean) => {
    setSidebarCollapsedState(collapsed);
    try { localStorage.setItem('krishiguard-sidebar', String(collapsed)); } catch (e) {}
  };

  return (
    <PreferencesContext.Provider value={{ theme, setTheme, density, setDensity, sidebarCollapsed, setSidebarCollapsed }}>
      <div className={density === 'compact' ? 'density-compact' : 'density-comfortable'}>
        {children}
      </div>
    </PreferencesContext.Provider>
  );
};

export const usePreferences = () => {
  const context = useContext(PreferencesContext);
  if (context === undefined) {
    throw new Error('usePreferences must be used within a PreferencesProvider');
  }
  return context;
};
