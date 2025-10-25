export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold text-center mb-8">
          🌾 АгроДанные КЗ
        </h1>
        <p className="text-center text-xl mb-4">
          Система управления фермерским хозяйством
        </p>
        <p className="text-center text-muted-foreground">
          Версия 2.0 - Modern Full-Stack
        </p>
        <div className="mt-8 flex justify-center gap-4">
          <a
            href="/login"
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
          >
            Войти
          </a>
          <a
            href="/api/v1/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="px-4 py-2 border border-border rounded-md hover:bg-accent"
          >
            API Docs
          </a>
        </div>
      </div>
    </main>
  )
}
