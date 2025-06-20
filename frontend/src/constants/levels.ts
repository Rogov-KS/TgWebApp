import { Level, Obstacle } from '../types/game';

export const LEVELS: Level[] = [
  {
    id: 'level-1',
    name: 'Начальный уровень',
    width: 20,
    height: 20,
    obstacles: [],
    foodTypes: ['normal', 'golden'],
    speed: 150,
    maxScore: 1000,
    isUnlocked: true,
  },
  {
    id: 'level-2',
    name: 'Стены',
    width: 20,
    height: 20,
    obstacles: [
      // Верхняя стена
      { position: { x: 5, y: 5 }, type: 'wall', isActive: true },
      { position: { x: 6, y: 5 }, type: 'wall', isActive: true },
      { position: { x: 7, y: 5 }, type: 'wall', isActive: true },
      { position: { x: 8, y: 5 }, type: 'wall', isActive: true },
      { position: { x: 9, y: 5 }, type: 'wall', isActive: true },
      { position: { x: 10, y: 5 }, type: 'wall', isActive: true },
      { position: { x: 11, y: 5 }, type: 'wall', isActive: true },
      { position: { x: 12, y: 5 }, type: 'wall', isActive: true },
      { position: { x: 13, y: 5 }, type: 'wall', isActive: true },
      { position: { x: 14, y: 5 }, type: 'wall', isActive: true },

      // Нижняя стена
      { position: { x: 5, y: 14 }, type: 'wall', isActive: true },
      { position: { x: 6, y: 14 }, type: 'wall', isActive: true },
      { position: { x: 7, y: 14 }, type: 'wall', isActive: true },
      { position: { x: 8, y: 14 }, type: 'wall', isActive: true },
      { position: { x: 9, y: 14 }, type: 'wall', isActive: true },
      { position: { x: 10, y: 14 }, type: 'wall', isActive: true },
      { position: { x: 11, y: 14 }, type: 'wall', isActive: true },
      { position: { x: 12, y: 14 }, type: 'wall', isActive: true },
      { position: { x: 13, y: 14 }, type: 'wall', isActive: true },
      { position: { x: 14, y: 14 }, type: 'wall', isActive: true },
    ],
    foodTypes: ['normal', 'golden', 'speed'],
    speed: 140,
    maxScore: 2000,
    isUnlocked: true,
  },
  {
    id: 'level-3',
    name: 'Лабиринт',
    width: 20,
    height: 20,
    obstacles: [
      // Вертикальные стены
      { position: { x: 8, y: 3 }, type: 'maze', isActive: true },
      { position: { x: 8, y: 4 }, type: 'maze', isActive: true },
      { position: { x: 8, y: 5 }, type: 'maze', isActive: true },
      { position: { x: 8, y: 6 }, type: 'maze', isActive: true },
      { position: { x: 8, y: 7 }, type: 'maze', isActive: true },

      { position: { x: 12, y: 12 }, type: 'maze', isActive: true },
      { position: { x: 12, y: 13 }, type: 'maze', isActive: true },
      { position: { x: 12, y: 14 }, type: 'maze', isActive: true },
      { position: { x: 12, y: 15 }, type: 'maze', isActive: true },
      { position: { x: 12, y: 16 }, type: 'maze', isActive: true },

      // Горизонтальные стены
      { position: { x: 3, y: 8 }, type: 'maze', isActive: true },
      { position: { x: 4, y: 8 }, type: 'maze', isActive: true },
      { position: { x: 5, y: 8 }, type: 'maze', isActive: true },
      { position: { x: 6, y: 8 }, type: 'maze', isActive: true },
      { position: { x: 7, y: 8 }, type: 'maze', isActive: true },

      { position: { x: 13, y: 12 }, type: 'maze', isActive: true },
      { position: { x: 14, y: 12 }, type: 'maze', isActive: true },
      { position: { x: 15, y: 12 }, type: 'maze', isActive: true },
      { position: { x: 16, y: 12 }, type: 'maze', isActive: true },
      { position: { x: 17, y: 12 }, type: 'maze', isActive: true },

      // Центральный блок
      { position: { x: 9, y: 9 }, type: 'maze', isActive: true },
      { position: { x: 10, y: 9 }, type: 'maze', isActive: true },
      { position: { x: 11, y: 9 }, type: 'maze', isActive: true },
      { position: { x: 9, y: 10 }, type: 'maze', isActive: true },
      { position: { x: 11, y: 10 }, type: 'maze', isActive: true },
      { position: { x: 9, y: 11 }, type: 'maze', isActive: true },
      { position: { x: 10, y: 11 }, type: 'maze', isActive: true },
      { position: { x: 11, y: 11 }, type: 'maze', isActive: true },
    ],
    foodTypes: ['normal', 'golden', 'speed', 'slow'],
    speed: 130,
    maxScore: 3000,
    isUnlocked: true,
  },
  {
    id: 'level-4',
    name: 'Ловушки',
    width: 20,
    height: 20,
    obstacles: [
      // Ловушки по периметру
      { position: { x: 0, y: 0 }, type: 'trap', isActive: true },
      { position: { x: 1, y: 0 }, type: 'trap', isActive: true },
      { position: { x: 2, y: 0 }, type: 'trap', isActive: true },
      { position: { x: 3, y: 0 }, type: 'trap', isActive: true },
      { position: { x: 4, y: 0 }, type: 'trap', isActive: true },

      { position: { x: 15, y: 0 }, type: 'trap', isActive: true },
      { position: { x: 16, y: 0 }, type: 'trap', isActive: true },
      { position: { x: 17, y: 0 }, type: 'trap', isActive: true },
      { position: { x: 18, y: 0 }, type: 'trap', isActive: true },
      { position: { x: 19, y: 0 }, type: 'trap', isActive: true },

      { position: { x: 0, y: 19 }, type: 'trap', isActive: true },
      { position: { x: 1, y: 19 }, type: 'trap', isActive: true },
      { position: { x: 2, y: 19 }, type: 'trap', isActive: true },
      { position: { x: 3, y: 19 }, type: 'trap', isActive: true },
      { position: { x: 4, y: 19 }, type: 'trap', isActive: true },

      { position: { x: 15, y: 19 }, type: 'trap', isActive: true },
      { position: { x: 16, y: 19 }, type: 'trap', isActive: true },
      { position: { x: 17, y: 19 }, type: 'trap', isActive: true },
      { position: { x: 18, y: 19 }, type: 'trap', isActive: true },
      { position: { x: 19, y: 19 }, type: 'trap', isActive: true },

      // Центральные ловушки
      { position: { x: 9, y: 9 }, type: 'trap', isActive: true },
      { position: { x: 10, y: 10 }, type: 'trap', isActive: true },
      { position: { x: 11, y: 11 }, type: 'trap', isActive: true },
      { position: { x: 8, y: 12 }, type: 'trap', isActive: true },
      { position: { x: 12, y: 8 }, type: 'trap', isActive: true },
    ],
    foodTypes: ['normal', 'golden', 'speed', 'slow', 'bonus'],
    speed: 120,
    maxScore: 5000,
    isUnlocked: false,
  },
  {
    id: 'level-5',
    name: 'Эксперт',
    width: 20,
    height: 20,
    obstacles: [
      // Сложный лабиринт
      { position: { x: 5, y: 5 }, type: 'wall', isActive: true },
      { position: { x: 6, y: 5 }, type: 'wall', isActive: true },
      { position: { x: 7, y: 5 }, type: 'wall', isActive: true },
      { position: { x: 8, y: 5 }, type: 'wall', isActive: true },
      { position: { x: 9, y: 5 }, type: 'wall', isActive: true },
      { position: { x: 10, y: 5 }, type: 'wall', isActive: true },
      { position: { x: 11, y: 5 }, type: 'wall', isActive: true },
      { position: { x: 12, y: 5 }, type: 'wall', isActive: true },
      { position: { x: 13, y: 5 }, type: 'wall', isActive: true },
      { position: { x: 14, y: 5 }, type: 'wall', isActive: true },

      { position: { x: 5, y: 14 }, type: 'wall', isActive: true },
      { position: { x: 6, y: 14 }, type: 'wall', isActive: true },
      { position: { x: 7, y: 14 }, type: 'wall', isActive: true },
      { position: { x: 8, y: 14 }, type: 'wall', isActive: true },
      { position: { x: 9, y: 14 }, type: 'wall', isActive: true },
      { position: { x: 10, y: 14 }, type: 'wall', isActive: true },
      { position: { x: 11, y: 14 }, type: 'wall', isActive: true },
      { position: { x: 12, y: 14 }, type: 'wall', isActive: true },
      { position: { x: 13, y: 14 }, type: 'wall', isActive: true },
      { position: { x: 14, y: 14 }, type: 'wall', isActive: true },

      // Вертикальные проходы
      { position: { x: 7, y: 7 }, type: 'maze', isActive: true },
      { position: { x: 7, y: 8 }, type: 'maze', isActive: true },
      { position: { x: 7, y: 9 }, type: 'maze', isActive: true },
      { position: { x: 7, y: 10 }, type: 'maze', isActive: true },
      { position: { x: 7, y: 11 }, type: 'maze', isActive: true },
      { position: { x: 7, y: 12 }, type: 'maze', isActive: true },

      { position: { x: 12, y: 7 }, type: 'maze', isActive: true },
      { position: { x: 12, y: 8 }, type: 'maze', isActive: true },
      { position: { x: 12, y: 9 }, type: 'maze', isActive: true },
      { position: { x: 12, y: 10 }, type: 'maze', isActive: true },
      { position: { x: 12, y: 11 }, type: 'maze', isActive: true },
      { position: { x: 12, y: 12 }, type: 'maze', isActive: true },

      // Ловушки
      { position: { x: 9, y: 9 }, type: 'trap', isActive: true },
      { position: { x: 10, y: 10 }, type: 'trap', isActive: true },
      { position: { x: 11, y: 11 }, type: 'trap', isActive: true },
      { position: { x: 8, y: 12 }, type: 'trap', isActive: true },
      { position: { x: 12, y: 8 }, type: 'trap', isActive: true },
    ],
    foodTypes: ['normal', 'golden', 'speed', 'slow', 'bonus'],
    speed: 100,
    maxScore: 10000,
    isUnlocked: false,
  },
];

export const getLevelById = (id: string): Level | undefined => {
  return LEVELS.find(level => level.id === id);
};

export const getNextLevel = (currentLevelId: string): Level | undefined => {
  const currentIndex = LEVELS.findIndex(level => level.id === currentLevelId);
  if (currentIndex === -1 || currentIndex === LEVELS.length - 1) {
    return undefined;
  }
  return LEVELS[currentIndex + 1];
};

export const unlockLevel = (levelId: string): void => {
  const level = LEVELS.find(l => l.id === levelId);
  if (level) {
    level.isUnlocked = true;
  }
};
