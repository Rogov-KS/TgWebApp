import React, { createContext, useContext, useState, ReactNode } from 'react';

export enum ModalType {
  NONE = 'NONE',
  AUTH = 'AUTH',
  LEADERBOARD = 'LEADERBOARD',
}

interface ModalContextType {
  currentModal: ModalType;
  setCurrentModal: (modal: ModalType) => void;
  isAnyModalOpen: boolean;
}

const ModalContext = createContext<ModalContextType | undefined>(undefined);

interface ModalProviderProps {
  children: ReactNode;
}

export function ModalProvider({ children }: ModalProviderProps) {
  const [currentModal, setCurrentModal] = useState<ModalType>(ModalType.NONE);

  const isAnyModalOpen = currentModal !== ModalType.NONE;

  return (
    <ModalContext.Provider value={{
      currentModal,
      setCurrentModal,
      isAnyModalOpen
    }}>
      {children}
    </ModalContext.Provider>
  );
}

export function useModal() {
  const context = useContext(ModalContext);
  if (context === undefined) {
    throw new Error('useModal must be used within a ModalProvider');
  }
  return context;
}
