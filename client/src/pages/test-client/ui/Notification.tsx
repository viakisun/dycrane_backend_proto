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
          <div className="bg-red-800 border border-red-600 text-white px-4 py-3 rounded-lg shadow-lg">
            <p className="font-bold">System Alert</p>
            <p className="text-sm">{error}</p>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
