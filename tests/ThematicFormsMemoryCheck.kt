package tribixbite.cleverkeys.langpack

import java.util.zip.ZipFile

/** Isolated real-pack gates with 16MiB ballast. Two v6-sized snapshots need 256MiB;
 * the single v7 snapshot and the original v5 -> expanded import retain 192MiB gates.
 * This is host JVM heap evidence, not an Android PSS or peak measurement.
 */
object ThematicFormsMemoryCheck {
    private fun pack(path: String): LanguageIntelligenceProvider = ZipFile(path).use { zip ->
        val manifest = zip.getInputStream(zip.getEntry("manifest.json")).reader(Charsets.UTF_8)
            .use(IntelligenceJson::document)
        zip.getInputStream(zip.getEntry(IntelligenceJson.FILE)).reader(Charsets.UTF_8).use {
            IntelligenceJson.parse(it, "pl", IntelligenceJson.integer(manifest, "version"),
                IntelligenceJson.capabilities(manifest))
        }
    }

    @JvmStatic fun main(args: Array<String>) {
        check(args.size in 1..2)
        val ballast = ByteArray(16 * 1024 * 1024)
        val before = if (args.size == 2) pack(args[0]) else null
        val after = pack(args.last())
        val previousVersion = before?.packageInfo()?.version
        check(previousVersion == null || previousVersion in listOf(5, 6))
        val cap = if (previousVersion == 6) 256 else 192
        check(Runtime.getRuntime().maxMemory() <= cap.toLong() * 1024 * 1024) { "Use -Xmx${cap}m or less" }
        check(after.packageInfo().version == 7)
        for (key in listOf("łódź", "malina", "maliną", "dodam", "grzeje", "kasami", "nawilżane",
            "odpowiadam", "patrzysz", "poczekaj", "podpowie", "pozdrawiam")) {
            check(after.lookup(key)?.sourceLemmas?.isNotEmpty() == true)
            before?.lookup(key)?.let { check(it == after.lookup(key)) }
        }
        check(after.lookup("backupy")?.sourceLemmas?.isNotEmpty() == true)
        check(after.lookup("backupy") != before?.lookup("backupy"))
        check(ballast.first() == 0.toByte() && ballast.last() == 0.toByte())
        println("Real ${if (before == null) "single v7" else "v$previousVersion + v7"} metadata + 16MiB ballast, ${cap}MiB heap: PASS")
    }
}
