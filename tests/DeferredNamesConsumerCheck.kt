package tribixbite.cleverkeys.langpack

import java.io.File
import java.util.zip.ZipFile
import tribixbite.cleverkeys.SwipeSurfaceVariants
import tribixbite.cleverkeys.swipe.geometric.CkdtDictionaryReader

/** Exact v9/v10 data and snapshot-reuse gates against the unchanged installed APK sources. */
object DeferredNamesConsumerCheck {
    private fun pack(path: String, previous: LanguageIntelligenceProvider? = null): LanguageIntelligenceProvider =
        ZipFile(path).use { z ->
            val manifest = z.getInputStream(z.getEntry("manifest.json")).reader(Charsets.UTF_8)
                .use(IntelligenceJson::document)
            val member = IntelligenceJson.declaration(manifest)!!
            check(member.schemaVersion == 2)
            z.getInputStream(z.getEntry(member.file)).reader(Charsets.UTF_8).use {
                IntelligenceJson.parse(it, "pl", IntelligenceJson.integer(manifest, "version"),
                    IntelligenceJson.capabilities(manifest), previous, member.schemaVersion)
            }
        }

    @JvmStatic fun main(args: Array<String>) {
        check(args.size == 4)
        val mode = args[0]
        check(mode in setOf("full", "cold", "replace", "repeat"))
        if (mode != "full") check(Runtime.getRuntime().maxMemory() <= 192L*1024*1024)
        val ballast = if (mode != "full") ByteArray(16*1024*1024) else null
        val old = when (mode) { "cold" -> null; "repeat" -> pack(args[2]); else -> pack(args[1]) }
        val new = pack(args[2], old)
        check(new.packageInfo().version == 10)
        if (old != null) check(old.sharedSources === new.sharedSources) { "Base source tables not reused" }
        for (key in listOf("łódź", "malina", "maliną", "grzeje", "poczekaj", "twitter", "usb")) {
            check(new.lookup(key)?.sourceLemmas?.isNotEmpty() == true)
            old?.lookup(key)?.let { check(it === new.lookup(key)) { "Unchanged entry duplicated: $key" } }
        }
        for (surface in listOf("Eleonora", "Jasio", "Ronalda", "Odessa", "Rutkowskiego", "Nosowska")) {
            val data = new.lookup(surface) ?: error("Missing new source form $surface")
            check(data.sourceLemmas.isNotEmpty())
            check(data.canonicalForm == surface)
            val shown = SwipeSurfaceVariants.expand(listOf(surface), listOf(100), listOf("pl"), new, false, false)
            check(shown.words.first() == surface && shown.scores.first() == 100)
        }
        if (mode == "full") {
            fun words(path: String) = ZipFile(path).use { z ->
                CkdtDictionaryReader.readEntries(z.getInputStream(z.getEntry("dictionary.bin")))
            }
            val before = words(args[1]); val after = words(args[2]); val indexed = after.associateBy { it.word.lowercase() }
            check(before.size == 190813 && after.size == 204463)
            check(indexed.size == after.size)
            var oldMetadata = 0
            for (word in before) {
                check(indexed[word.word.lowercase()] == word) { "Changed canonical spelling or rank: ${word.word}" }
                val previous = old!!.lookup(word.word)
                val current = new.lookup(word.word)
                check(previous == current) { "Changed old metadata: ${word.word}" }
                if (previous != null) {
                    oldMetadata++
                    check(previous === current) { "Old immutable entry not reused: ${word.word}" }
                }
            }
            check(oldMetadata == 100649)
            val oldKeys = before.map { it.word.lowercase() }.toSet()
            val checked = HashSet<String>()
            File(args[3]).useLines(Charsets.UTF_8) { lines ->
                lines.forEach { line ->
                    val value = IntelligenceJson.document(line.reader())
                    val key = IntelligenceJson.string(value, "surfaceKey")
                    check(key !in oldKeys && checked.add(key))
                    // Unencoded native-source expectation uses the independent legacy reader.
                    val root = """{"schemaVersion":1,"languageCode":"pl","entries":[$line]}"""
                    val expected = IntelligenceJson.parse(root.reader(), "pl", 10, setOf("metadata", "capitalization")).lookup(key)!!
                    check(expected == new.lookup(key)) { "Shared decoding changed source data: $key" }
                    check(expected.sourceLemmas.isNotEmpty())
                    check(indexed[key]!!.word == (expected.canonicalForm ?: key))
                }
            }
            check(checked == indexed.keys - oldKeys && checked.size == 13650)
            for (choices in listOf(listOf("malina", "maliną", "mamoną"), listOf("łódź", "łodzi", "lód"),
                listOf("praca", "pracą", "pracy"), listOf("Twitter", "Twittera", "Instagram"))) {
                for (capital in listOf(false, true)) check(
                    SwipeSurfaceVariants.expand(choices, listOf(100,80,60), listOf("pl","pl","pl"), old, capital, false) ==
                    SwipeSurfaceVariants.expand(choices, listOf(100,80,60), listOf("pl","pl","pl"), new, capital, false))
            }
            println("Real v9/v10 PASS: 190813 old records/ranks and 100649 immutable metadata views retained; 13650 native-source additions; 204463 total words")
        } else {
            check(ballast!!.first() == 0.toByte() && ballast.last() == 0.toByte())
            println("Real deferred names $mode +16MiB ballast at192MiB PASS")
        }
    }
}
