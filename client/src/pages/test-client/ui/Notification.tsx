import React from 'react';
import { useWorkflowStore } from '../state/workflowStore';
import { motion, AnimatePresence } from 'framer-motion';

export const Notification: React.FC = () => {
  const { error, actions } = useWorkflowStore();

  return (
    <AnimatePresence>
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -50 }}
          className="fixed top-20 right-4 z-50 cursor-pointer"
          onClick={() => actions.setError(null)}
        >
          <div className="bg-red-900/50 backdrop-blur-sm border border-red-500 text-red-300 px-6 py-4 rounded-lg shadow-neon-magenta">
            <p className="font-bold uppercase">System Alert</p>
            <p>{error}</p>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
