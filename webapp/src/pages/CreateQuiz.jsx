export default function CreateQuiz() {
  return (
    <div className="p-6 text-white bg-black min-h-screen">
      <h1 className="text-3xl mb-5 font-bold">
        ➕ Create Quiz
      </h1>

      <input
        placeholder="Question"
        className="w-full p-4 rounded-xl bg-zinc-900 mb-4"
      />

      <input
        placeholder="Option 1"
        className="w-full p-4 rounded-xl bg-zinc-900 mb-3"
      />

      <input
        placeholder="Option 2"
        className="w-full p-4 rounded-xl bg-zinc-900 mb-3"
      />

      <input
        placeholder="Option 3"
        className="w-full p-4 rounded-xl bg-zinc-900 mb-3"
      />

      <input
        placeholder="Option 4"
        className="w-full p-4 rounded-xl bg-zinc-900 mb-3"
      />

      <button className="bg-blue-600 px-6 py-3 rounded-xl mt-4">
        Save Quiz
      </button>
    </div>
  )
}