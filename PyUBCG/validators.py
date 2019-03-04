"""Module with config schema to validate it"""

import trafaret as tr

CONFIG_SCHEMA = tr.Dict({
    tr.Key('general'):
        tr.Dict({
            'project_name': tr.String(),
            'config': tr.String(),
            'processes': tr.Int(),
        }),
    tr.Key('paths'):
        tr.Dict({
            'project_folder': tr.String(),
            'fasta_input_folder': tr.String(),
            'extract_output': tr.String(),
            'prodigal_output': tr.String(),
            'prodigal_nuc': tr.String(),
            'prodigal_pro': tr.String(),
            'hmmsearch_output': tr.String(),
            'bcg_dir': tr.String(),
            'align_mafft_output': tr.String(),
            'align_output': tr.String(),
            'align_input_merge': tr.String(),
            'align_input_parse': tr.String(),
            'align_filtering_output': tr.String(),
            'align_align_output': tr.String(),
            'align_alignment_output': tr.String(),
        }),
    tr.Key('prefixes'):
        tr.Dict({
            'nuc_prefix': tr.String(),
            'pro_prefix': tr.String(),
            'nuc_input': tr.String(),
            'pro_input': tr.String(),
            'align_prefix': tr.String(allow_blank=True),
        }),
    tr.Key('postfixes'):
        tr.Dict({
            'nuc_input_const': tr.String(),
            'pro_input_const': tr.String(),
            'input_parsing_dna_const': tr.String(),
            'input_parsing_pro_const': tr.String(),
            'mafft_res_pro_const': tr.String(),
            'mafft_res_dna_const': tr.String(),
            'align_align_const': tr.String(),
            'align_concateneted': tr.String(),
        }),
    tr.Key('tools'):
        tr.Dict({
            'prodigal_like_tool': tr.String(),
            'hmmsearch_like_tool': tr.String(),
            'mafft_like_tool': tr.String(),
            'align_tool': tr.String(),
        }),
    tr.Key('biological'):
        tr.Dict({
            'prodigal_translation_table': tr.Int(),
            'ubcg_gene': tr.List(tr.String),
            'hmm_base': tr.String(),
        }),
})
