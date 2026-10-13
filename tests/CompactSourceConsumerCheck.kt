package tribixbite.cleverkeys.langpack

import java.util.zip.ZipFile
import tribixbite.cleverkeys.SwipeSurfaceVariants
import tribixbite.cleverkeys.swipe.geometric.CkdtDictionaryReader

/** Actual v10/v11 cold, semantic snapshot reuse and repeat loads; not Android PSS. */
object CompactSourceConsumerCheck {
    private fun pack(path: String, previous: LanguageIntelligenceProvider? = null): LanguageIntelligenceProvider =
        ZipFile(path).use { z ->
            val m = z.getInputStream(z.getEntry("manifest.json")).reader(Charsets.UTF_8).use(IntelligenceJson::document)
            val member = IntelligenceJson.declaration(m)!!
            z.getInputStream(z.getEntry(member.file)).reader(Charsets.UTF_8).use {
                IntelligenceJson.parse(it, "pl", IntelligenceJson.integer(m,"version"), IntelligenceJson.capabilities(m), previous, member.schemaVersion)
            }
        }
    @JvmStatic fun main(args: Array<String>) {
        check(args.size == 3)
        val mode = args[0]
        if (mode != "full") check(Runtime.getRuntime().maxMemory() <= 192L*1024*1024)
        val ballast = if (mode != "full") ByteArray(16*1024*1024) else null
        val old = when(mode) { "cold" -> null; "repeat" -> pack(args[2]); else -> pack(args[1]) }
        val after = pack(args[2], old)
        check(after.packageInfo().version == 11)
        old?.sharedSources?.let { check(after.sharedSources!!.extendsTables(it)) }
        for (key in listOf("łódź", "malina", "maliną", "praca", "grzeje", "poczekaj", "twitter", "usb", "eleonora", "rutkowskiego")) {
            check(after.lookup(key)?.sourceLemmas?.isNotEmpty() == true)
            old?.lookup(key)?.let { check(it === after.lookup(key)) { "Old semantic entry duplicated: $key" } }
        }
        if(mode == "full") {
            fun binary(path: String) = ZipFile(path).use { z -> z.getInputStream(z.getEntry("dictionary.bin")).readBytes() }
            val bytes = binary(args[1]); check(bytes.contentEquals(binary(args[2])))
            val words = CkdtDictionaryReader.readEntries(bytes)
            check(words.size == 204463)
            // Also compare a cold compact snapshot; replacement reuse cannot hide decoding errors.
            val cold = pack(args[2]); var metadata = 0
            for (word in words) {
                val expected = old!!.lookup(word.word)
                check(expected == cold.lookup(word.word)) { "Compact source data changed: ${word.word}" }
                check(expected == after.lookup(word.word))
                if(expected != null) { metadata++; check(expected === after.lookup(word.word)) }
            }
            check(metadata == 114299)
            for(choices in listOf(listOf("malina","maliną","mamoną"),listOf("łódź","łodzi","lód"),
                listOf("praca","pracą","pracy"),listOf("Twitter","Twittera","Instagram"))) {
                for(cap in listOf(false,true)) check(
                    SwipeSurfaceVariants.expand(choices,listOf(100,80,60),listOf("pl","pl","pl"),old,cap,false) ==
                    SwipeSurfaceVariants.expand(choices,listOf(100,80,60),listOf("pl","pl","pl"),cold,cap,false))
            }
            println("Real v10/v11 PASS: 204463 identical CKDT words/ranks; 114299 exact cold metadata views/source identities and reused upgrade entries; presentation unchanged")
        } else {
            check(ballast!!.first()==0.toByte() && ballast.last()==0.toByte())
            println("Real compact source $mode +16MiB ballast at192MiB PASS")
        }
    }
}
