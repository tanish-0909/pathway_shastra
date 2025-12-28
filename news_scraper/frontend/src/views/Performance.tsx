import { motion } from 'framer-motion'

export function Performance() {
  return (
    <motion.div 
      className="h-full p-6 bg-background"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <h1 className="text-2xl font-semibold text-foreground mb-4">Performance</h1>
      <div className="bg-card border border-border rounded-lg p-6">
        <p className="text-muted-foreground">Performance view coming soon...</p>
      </div>
    </motion.div>
  )
}
