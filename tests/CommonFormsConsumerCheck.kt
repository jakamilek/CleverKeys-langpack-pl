package tribixbite.cleverkeys.langpack

import java.io.File
import java.util.Locale
import java.util.zip.ZipFile
import tribixbite.cleverkeys.swipe.geometric.CkdtDictionaryReader

/** Compile with the actual consumer files, never a Python imitation of its parser. */
fun main(args: Array<String>) {
    fun pack(path: String): Pair<List<CkdtDictionaryReader.Entry>, LanguageIntelligenceProvider> =
        ZipFile(File(path)).use { zip ->
            val manifest = zip.getInputStream(zip.getEntry("manifest.json")).reader(Charsets.UTF_8)
                .use(IntelligenceJson::document)
            val bytes = zip.getInputStream(zip.getEntry("dictionary.bin")).use { it.readBytes() }
            val words = CkdtDictionaryReader.readEntries(bytes)
            check(words.size == IntelligenceJson.integer(manifest, "wordCount"))
            val provider = zip.getInputStream(zip.getEntry(IntelligenceJson.FILE)).reader(Charsets.UTF_8).use {
                IntelligenceJson.parse(it, "pl", IntelligenceJson.integer(manifest, "version"),
                    IntelligenceJson.capabilities(manifest))
            }
            words to provider
        }
    val (before, oldProvider) = pack(args[0])
    val (after, provider) = pack(args[1])
    val old = before.associateBy { it.word.lowercase(Locale.ROOT) }
    val all = after.associateBy { it.word.lowercase(Locale.ROOT) }
    check(all.size == after.size && after.size > before.size)
    for ((key, word) in old) {
        check(all[key] == word) { "Old spelling/rank changed" }
        oldProvider.lookup(key)?.let { check(provider.lookup(key) == it) { "Old metadata changed" } }
    }
    val lemmas = mutableMapOf<SourceLemma, String>()
    var shared = 0
    for (word in after) {
        val key = word.word.lowercase(Locale.ROOT)
        if (key in old) continue
        val data = provider.lookup(key) ?: error("Missing new source metadata")
        check(data.sourceLemmas.isNotEmpty()) { "No bounded source identity for $key" }
        for (lemma in data.sourceLemmas) {
            val prior = lemmas.putIfAbsent(lemma, key)
            if (prior != null && prior != key) {
                check(provider.sharesSourceLemma(prior, key))
                shared++
            }
        }
    }
    check(shared > 0)
    for (key in listOf("dodam", "grzeje", "kasami", "nawilżane", "odpowiadam",
        "patrzysz", "poczekaj", "podpowie", "pozdrawiam")) {
        check(key in all && provider.lookup(key)?.sourceLemmas?.isNotEmpty() == true)
    }
    println("Actual JVM consumer PASS: ${before.size} old records retained; ${after.size} total; $shared shared-source relations")
}
