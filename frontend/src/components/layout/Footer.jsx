const Footer = () => {
  return (
    <footer className="mt-auto border-t border-border bg-surface">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
          <div>
            <h3 className="mb-3 text-sm font-bold text-foreground">Edu Assist</h3>
            <p className="text-sm text-muted">
              Adaptive diagnostic learning aligned to Nepal CDC curriculum.
            </p>
          </div>
          <div>
            <p className="ds-mono-label mb-3">Platform</p>
            <ul className="space-y-2 text-sm text-muted">
              <li><a href="/assessment" className="transition-colors hover:text-primary">Assessments</a></li>
              <li><a href="/resources" className="transition-colors hover:text-primary">Roadmap</a></li>
              <li><a href="/my-progress" className="transition-colors hover:text-primary">Progress</a></li>
            </ul>
          </div>
          <div>
            <p className="ds-mono-label mb-3">Support</p>
            <p className="text-sm text-muted">support@eduassist.np</p>
          </div>
        </div>
        <div className="ds-divider mt-8 pt-6 text-center">
          <p className="font-mono text-[10px] uppercase tracking-widest text-muted">
            © 2025 Edu Assist · Nepal CDC Grades 6–10
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
