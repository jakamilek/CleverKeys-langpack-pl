package tribixbite.cleverkeys.langpack
import java.io.File
import java.util.zip.ZipFile
import com.google.gson.JsonParser

/** Runs the unchanged accepted v11 reader, not an APK build. */
object ExternalLemmaConsumerCheck {
 @JvmStatic fun main(args: Array<String>) {
  check(args.size == 4)
  val old = ZipFile(args[0]).use { z -> z.getInputStream(z.getEntry("language-intelligence.json")).reader(Charsets.UTF_8).use {
   IntelligenceJson.parse(it, "pl", 11, setOf("metadata", "capitalization"), null, 3)
  }}
  val updated = File(args[1]).reader(Charsets.UTF_8).use {
   IntelligenceJson.parse(it,"pl",11,setOf("metadata", "capitalization"),old,3)
  }
  var retained=0
  File(args[3]).forEachLine { key ->
   check(old.lookup(key) != null && old.lookup(key) === updated.lookup(key)) { "Changed existing metadata: $key" }
   retained++
  }
  check(retained==114299)
  val expected=JsonParser.parseString(File(args[2]).readText()).asJsonArray
  check(expected.size()==8)
  for(raw in expected) {
   val e=raw.asJsonObject;val key=e["surfaceKey"].asString
   check(old.lookup(key)==null)
   val got=updated.lookup(key)!!
   check(JsonParser.parseString(got.metadataJson)==e["metadata"]) { "Lost evidence: $key" }
   check(got.sourceLemmas.isNotEmpty())
  }
  for((a,b) in listOf("powerbank" to "powerbanki", "streaming" to "streamingu", "googlować" to "googluje", "streamować" to "streamuje")) {
   check(updated.sharesSourceLemma(a,b)) { "Missing relation: $a / $b" }
  }
  check(!updated.sharesSourceLemma("streaming","streamować"))
  check(!updated.sharesSourceLemma("powerbank","smartfon"))
  for(key in listOf("streamować","streamuje")) {
   val metadata=JsonParser.parseString(updated.lookup(key)!!.metadataJson).asJsonObject
   val facts=metadata["externalLexicalEvidence"].asJsonArray
   check(facts.size()==2)
   check(facts.map { it.asJsonObject["senseId"].asString }.toSet().size==2)
   check(metadata["externalReadingLinks"].asJsonArray.size()==2)
  }
  println("PASS: 8 source-linked entries, 4 positive and 2 negative lemma pairs, 2 distinct streamować senses, 114299 v11 entries retained unchanged")
 }
}
