package tribixbite.cleverkeys.langpack

import java.util.zip.ZipFile
import tribixbite.cleverkeys.SwipeSurfaceVariants

/** Real v8 metadata, both cold and replacing the accepted v7 snapshot. This
 * measures host JVM heap capacity, not Android PSS, peak memory or swipe accuracy.
 */
object NamesFormsMemoryCheck {
    private fun pack(path: String, previous: LanguageIntelligenceProvider? = null): LanguageIntelligenceProvider =
        ZipFile(path).use { zip ->
            val manifest = zip.getInputStream(zip.getEntry("manifest.json")).reader(Charsets.UTF_8)
                .use(IntelligenceJson::document)
            zip.getInputStream(zip.getEntry(IntelligenceJson.FILE)).reader(Charsets.UTF_8).use {
                IntelligenceJson.parse(it, "pl", IntelligenceJson.integer(manifest, "version"),
                    IntelligenceJson.capabilities(manifest), previous)
            }
        }

    @JvmStatic fun main(args: Array<String>) {
        check(args.size in 1..2)
        check(Runtime.getRuntime().maxMemory() <= 192L * 1024 * 1024) { "Use -Xmx192m or less" }
        val ballast = ByteArray(16 * 1024 * 1024)
        val before = if (args.size == 2) pack(args[0]) else null
        check(before == null || before.packageInfo().version == 7)
        val after = pack(args.last(), before)
        check(after.packageInfo().version == 8)
        for (key in listOf("łódź", "malina", "maliną", "dodam", "grzeje", "kasami", "nawilżane",
            "odpowiadam", "patrzysz", "poczekaj", "podpowie", "pozdrawiam", "backupy")) {
            check(after.lookup(key)?.sourceLemmas?.isNotEmpty() == true)
            before?.lookup(key)?.let { check(it === after.lookup(key)) { "Old immutable entry not shared: $key" } }
        }
        // Exact source case and related decoded forms survive the actual presentation layer.
        for (surface in listOf("USB", "HTML", "NATO", "Google", "Twitter", "Instagram", "Jana")) {
            val data = after.lookup(surface) ?: error("Missing source form $surface")
            check(data.canonicalForm == surface && data.sourceLemmas.isNotEmpty())
            val slate = SwipeSurfaceVariants.expand(listOf(surface), listOf(123), listOf("pl"),
                after, capitalize = false, capsLock = false)
            check(slate.words == listOf(surface) && slate.scores == listOf(123))
        }
        check(after.sharesSourceLemma("Twitter", "Twittera"))
        val related = SwipeSurfaceVariants.expand(listOf("Twitter", "Twittera"), listOf(123, 99),
            listOf("pl", "pl"), after, capitalize = false, capsLock = false)
        check(related.words == listOf("Twitter", "Twittera") && related.scores == listOf(123, 99))
        check(after.lookup("janowi")?.capitalization?.defaultSurface == "janowi")
        check(ballast.first() == 0.toByte() && ballast.last() == 0.toByte())
        println("Real ${if (before == null) "cold v8" else "v7 + shared v8"} metadata + 16MiB ballast, 192MiB heap: PASS")
    }
}
